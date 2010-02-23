#!/usr/bin/env python -OO
# encoding: utf-8

###########
# ORP - Open Robotics Platform
#
# Copyright (c) 2010 John Harrison, William Woodall
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##########

"""
rpcserver.py - Contains the RPCServer class which defines the available \
functions in the rpc server.

Created by William Woodall on 2010-09-18.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import os
import sys
import types
import signal
from multiprocessing import Process, Lock, Value, Queue
from threading import Timer
from SimpleXMLRPCServer import SimpleXMLRPCServer
import time
import logging
import ctypes

# Other Libraries
import orpd
from orpd import network_handlers
import orpdaemon
from logerror import logError
from sandbox import Sandbox

###  Class  ###

class RPCServer(SimpleXMLRPCServer):
    """Defines the available xmlrpc functions"""
    def __init__(self, connection, daemon):
        """docstring for __init__"""
        # Setup logging
        self.log = logging.getLogger('ORPD')
        self.log_servers = []
        self.daemon = daemon
        self.sandbox = None
        self.sandbox_proc = None
        self.sandbox_lock = None
        self.sandbox_queue = None
        self.sandbox_running = None
        self.sandbox_paused = False
        self.client_addr = None
        self.network_handlers = network_handlers
        SimpleXMLRPCServer.__init__(self,
                        connection, logRequests=False, allow_none=True)
    
    def _dispatch(self, method, params):
        """Overrides the dispatch method"""
        try:
            # We are forcing the 'xmlrpc_' prefix on methods that are
            # callable through XML-RPC
            func = getattr(self, 'xmlrpc_'+method)
        except AttributeError:
            try:
                func = self.funcs[method]
                if func is not None:
                    try:
                        return func(*params)
                    except Exception as err:
                        logError(sys.exc_info(), self.log.error, 'Exception in RPC call %s' % method, orpdaemon.HWM_MAGIC_LINENO)
                else:
                    raise Exception("Method '%s' is not supported by this Server" % method)
            except Exception:
                return SimpleXMLRPCServer._dispatch(self, method, params)
        else:
            try:
                return func(*params)
            except Exception as err:
                logError(sys.exc_info(), self.log.error, "Exception in RPC call %s" % method)
    
    def registerFunctions(self, functions):
        """Takes a dictionary, functions, and registers them"""
        for func_name in functions:
            self.register_function(functions[func_name], func_name)
    
    def verify_request(self, request, client_addr):
        """Overrides SimpleXMLRPCServer.verify_request to 
        capture the address of the latest request"""
        self.client_addr = client_addr
        return True
    
    def xmlrpc_listFunctions(self):
        """Lists the Available Functions"""
        methods = self.funcs.keys()
        for x in ['system.listMethods', 'system.methodHelp', 'system.methodSignature']:
            if x in methods:
                methods.remove(x)
        return methods
    
    ####  Functions Related to Executing Control Code  ####
    def xmlrpc_runControlCode(self, control_code=None):
        """Runs control code in the files dir"""
        # Check for correct parameters
        if control_code == None:
            self.log.error("No Control Code passed to function runControlCode")
            return False
        if self.sandbox_proc != None and self.sandbox_proc.is_alive():
            self.log.error("Control Code already running")
            return False
        if not os.path.exists(control_code):
            self.log.error('Control Code not found: ' + control_code)
            return False
        # Spawn the sandbox
        self.sandbox = Sandbox()
        self.sandbox_lock = Lock()
        self.sandbox_running = Value(ctypes.c_bool, True)
        self.sandbox_queue = Queue()
        self.sandbox_proc = \
            Process("Sandbox", target=self.sandbox.startUp,
                args=(self.daemon.device_objects, self.daemon.work_directory, 
                        control_code, self.sandbox_lock, self.sandbox_running, 
                        self.sandbox_queue))
        self.sandbox_proc.start()
        Timer(0.5, self.joinControlCode).start()
        # Attempt to call start() on each of the devices that are running
        for device in self.daemon.device_objects:
            try:
                device.start()
            except Exception as error:
                logError(sys.exc_info(), self.log.error, "Error executing start() of the %s device:" % device.name, orpdaemon.HWM_MAGIC_LINENO)
        return True

    def joinControlCode(self):
        """This function trys to join the sandbox and periodically checks to see if it has crashed"""
        # Wait for the sandbox to stop
        try:
            sandbox_running = True
            while sandbox_running:
                if self.sandbox_proc != None and self.sandbox_proc.exitcode == None:
                    pass
                else:
                    sandbox_running = False
                    self.sandbox_running.value = False
                    break
                self.sandbox_proc.join(1)
        finally:
            if self.sandbox_proc.exitcode == -signal.SIGTERM:
                result = False
                self.log.info('Control Code did not exit cleanly')
            self.sandbox = None
            self.sandbox_proc = None
            self.sandbox_lock = None
            self.sandbox_running.value = False
            self.sandbox_paused = False
            for device in self.daemon.device_objects:
                try:
                    device.stop()
                except Exception as error:
                    logError(sys.exc_info(), self.log.error, "Error executing stop() of the %s device:" % device.name, orpdaemon.HWM_MAGIC_LINENO)
            self.log.info('Control Code Stopped')

    def xmlrpc_stopControlCode(self):
        """Stops the sandbox, returns false if it times out"""
        self.log.info('Control Code Stopping')
        # Check to see if it is already stopped
        result = True
        if self.sandbox_proc == None or not self.sandbox_proc.is_alive():
            return result
        # Start a timer to kill the sandbox is necessary
        Timer(2, self.sandbox_proc.terminate).start()
        # Stop the sandbox
        self.sandbox_running.value = False
        self.sandbox_proc.join()
        if self.sandbox_proc.exitcode == -signal.SIGTERM:
            result = False
        return result
    
    def xmlrpc_pauseControlCode(self):
        """Pauses the current running control, if some is running"""
        # Check that control code is running, else return False
        if self.sandbox_proc == None:
            return False
        # Pause the control code
        if not self.sandbox_paused:
            self.sandbox_lock.acquire()
            self.sandbox_paused = True
        return True
    
    def xmlrpc_resumeControlCode(self):
        """Pauses the current running control, if some is running"""
        # Check that control code is running, else return False
        if self.sandbox_proc == None or not self.sandbox_paused:
            return False
        # Resume the control code
        # self.sandbox_lock.acquire(0)
        self.sandbox_lock.release()
        self.sandbox_paused = False
        return True
    
    ####  Functions related to logging  ####
    def xmlrpc_log(self, level, msg):
        """Allows for people to inject logs over rpc"""
        if type(level) == str:
            levels = {'notset':0,'debug':10,'info':20,
                      'warning':30,'error':40,'critical':50}
            self.log.log(levels[level.lower()], msg)
        elif type(level) == int:
            self.log.log(level, msg)
    
    def xmlrpc_debug(self, msg):
        """Creates a debug log"""
        self.log.debug(msg)
    
    def xmlrpc_info(self, msg):
        """Creates an info log"""
        self.log.info(msg)
    
    def xmlrpc_warning(self, msg):
        """Creates a warning log"""
        self.log.warning(msg)
    
    def xmlrpc_error(self, msg):
        """Creates an error log"""
        self.log.error(msg)
    
    def xmlrpc_critical(self, msg):
        """Creates a critical log"""
        self.log.critical(msg)
    
    ####  File Management Functions  ####
    def xmlrpc_write(self, file_name, file_contents, timestamp=None):
        """Writes a file sent to the daemon,
        returns True on success and False on failure"""
        file_dir, _ = os.path.split(file_name)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir)
        result = True
        try:
            save_file = open(file_name, 'w+')
            save_file.write(file_contents)
            save_file.close()
            if timestamp:
                os.utime(file_name, (timestamp, timestamp))
            self.log.info('Wrote file '+file_name)
        except IOError as error:
            self.log.error('Cannot write file: '+file_name+\
                                    '\n'+str(error))
            result = False
        return result

    def xmlrpc_getFileContents(self, file_name):
        """Returns the contents of the given file"""
        file_handler = open(file_name, 'r')
        return file_handler.read()

    def xmlrpc_getConfig(self):
        """This function returns the config file as a string"""
        config_file = open(self.daemon.config_file_name, 'r')
        return config_file.read()
        
    def xmlrpc_sendConfig(self, config):
        """Writes the given data to the config file"""
        config_file_name = self.daemon.config_file_name
        _, temp_name = os.path.split(config_file_name)
        if temp_name == 'orpd.cfg.default':
            self.daemon.config_file_name = config_file_name = config_file_name[:-8]
        config_file = open(config_file_name, 'w+')
        config_file.write(config)
        config_file.close()

    ####  Misc Functions  ####
    def xmlrpc_ping(self):
        """Ping, Pong."""
        self.log.info('Pong')
        return True

    def xmlrpc_connect(self):
        """Called when a dashboard connects"""
        self.log.info('Receiving connection from %s' % self.client_addr[0])
        if self.client_addr[0] in self.network_handlers:
            self.log.debug('Dashboard Already Connected, not opening a new logging socket')
        else:
            # Setup Network handler
            network = logging.handlers.SocketHandler(self.client_addr[0],
                                logging.handlers.DEFAULT_TCP_LOGGING_PORT)
            network.setLevel(logging.DEBUG)
            root = logging.getLogger('')
            root.addHandler(network)
            self.log_servers.append(network)
            self.network_handlers[self.client_addr[0]] = network
    
    def xmlrpc_fileSync(self):
        "Synchronize the files between the server and the client"
        return self.__buildListing()
        
    def __buildListing(self):
        """Build a listing of the files in files and modules for connection"""
        cc_list = self.__walkDirectory(os.path.join(
            self.daemon.work_directory, 'files'))
        module_list = self.__walkDirectory(os.path.join(
            self.daemon.work_directory, 'modules'))
        return (cc_list, module_list)

    def __walkDirectory(self, path):
        """Walks the Directory"""
        listing = {}
        for root, _, files in os.walk(path):
            # if root[0] == '.':
                # continue
            file_path = root.replace(path, '')[1:]
            if file_path and filter(lambda x: x[0] == '.', file_path.split(os.sep)):
                continue
            for f in files:
                if f[0] != '.' and not f.endswith(('.hwmo', '.hwmc', '.pyo', '.pyc', '.cco', '.ccc')):
                    full_path = os.path.join(path, file_path, f)
                    listing_name = os.path.join(file_path, f)
                    listing[listing_name] = os.stat(full_path)[8]
        return listing

    def xmlrpc_disconnect(self):
        """docstring for xmlrpc_disconnect"""
        if self.client_addr[0] in self.network_handlers:
            root = logging.getLogger()
            root.removeHandler(self.network_handlers[self.client_addr[0]])
            del self.network_handlers[self.client_addr[0]]

    def xmlrpc_shutdown(self):
        """Shutsdown the system"""
        # I do this so that the xmlrpc function can return properly.
        # If you just xmlrpc.shutdown() then,
        # the return None line never gets executed.
        # So I just have it call that 100mS later to allow it to return first.
        Timer(0.1, self.__shutdown).start()
        return None
        
    def xmlrpc_restart(self):
        """Restarts the server"""
        self.log.info('Server Restarted')
        return self.xmlrpc_changeWorkDirectory(self.daemon.work_directory)

    def xmlrpc_changeWorkDirectory(self, work_dir):
        """This stops the services, changes the work directory,
        and then reloads everything that can be configured through config files"""
        if os.path.exists(work_dir):
            self.daemon.new_work_dir = work_dir
            self.xmlrpc_shutdown()
            return True
        return False

    def __shutdown(self):
        """Shuts down"""
        self.shutdown()
        self.socket.close()
