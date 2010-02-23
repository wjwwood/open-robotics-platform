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
sandbox.py - Used to start and execute control code

Created by William Woodall on 2010-09-29.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import os
import os.path
import imp
import sys
import signal
import threading
import traceback
import logging
import logging.handlers
import xmlrpclib
import re
from multiprocessing import Queue
# from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Timer
from event_system import Event, MultiLevelEventQueue

# ORP Libs
from logerror import logError
from lib import importspecial

###  Functions  ###
def signalShutdown(signal, frame):
    """Handles the SIGINT signal, shutting everything down"""
    logging.getLogger('Sandbox').info('Caught SIGINT signal')
    exit(1)

def tracer(frame, event, args):
    """This function gets called every time a line of cc is executed"""
    global lck
    lck.acquire()
    lck.release()
    return tracer

###  Classes  ###
class Proxy(object):
    pass

class EventRetriever(threading.Thread):
    """A thread that simply gets the events from the shared queue and 
    formats them a bit. It's simply a producer thread."""
    def __init__ (self, running, queue, log, lock, mleq):
        ""
        threading.Thread.__init__(self)
        self.running = running
        self.queue = queue
        self.log = log
        self.lock = lock
        self.mleq = mleq
    
    def run(self):
        """Overrides the run funtion in Thread"""
        while self.running.value:
            try:
                evt = self.queue.get(True, 1)
            except Exception as error:
                pass
            else:
                with self.lock:
                    self.mleq.addEvent(Event(evt[0], evt[1], evt[2]))
    

class ProxyLogger(object):
    """Proxy Logger that checks to make sure that logs get str()'ed before propagating"""
    def __init__(self, logger):
        self.logger = logger
    
    def log(self, level, msg):
        """Posts a msg at a level to the logger"""
        str_msg = str(msg)
        self.logger.log(level, str_msg)
    
    def debug(self, msg):
        """Logs a Debug Message"""
        self.log(10, msg)
    
    def info(self, msg):
        """Logs a Info Message"""
        self.log(20, msg)
    
    def warning(self, msg):
        """Logs a Warning Message"""
        self.log(30, msg)
    
    def error(self, msg):
        """Logs a Error Message"""
        self.log(40, msg)
    
    def critical(self, msg):
        """Logs a Critical Message"""
        self.log(50, msg)
    

class Sandbox(object):
    """Contains functions and data common to the sandbox"""
    def __init__(self):
        self.hardware_modules_services = []
        self.root_log = None
        self.orpd_server = None
        self.log = None
        self.timer = None
        self.server = None
        self.queue = None
        self.evt_handler = None
        self.lock = threading.Lock()
        self.mleq = None

    def executeControlCode(self, file_name, glbls, lcls):
        """Function to facilitate execution of control code"""
        # Get the path and module name
        path, module_name = os.path.split(file_name)
        # import the module
        try:
            module = importspecial.importOverride(module_name[:-3])
            # inject more things into the namespace that provide extended funtionality
            for name, ptr in glbls.items():
                setattr(module, name, ptr)
            # Start the HWM (Device) specified Services
            self.startDeviceServices()
            # Turn on import override
            importspecial.overrideImport()
            # Call Main
            module.main()
            # Catch any runtime exceptions in the control code
        except Exception as error:
            logError(sys.exc_info(), self.log.error, 'Control Code Exception:', importspecial.MAGIC_LINENO)
        finally:
            # Turn off import overriding
            importspecial.restoreImport()
    
    def extractLocals(self, local_vars, methods):
        """Extracts Local Variables"""
        obj_cache = {}
        for method in methods:
            method_name = str(method)
            if '.' in method:
                obj_array = method.split('.')
                method = obj_array.pop(0)
                if method in obj_cache:
                    cur = var = obj_cache[method]
                else:
                    obj_cache[method] = cur = var = Proxy()
                actual_func = obj_array.pop()
                full_name = str(method)
                for part in obj_array:
                    full_name = full_name + part
                    if full_name in obj_cache:
                        cur = obj_cache[full_name]
                    else:
                        setattr(cur, part, Proxy())
                        obj_cache[full_name] = cur = getattr(cur, part)
                setattr(cur, actual_func, getattr(self.orpd_server, method_name))
            local_vars.update({method : var})
        return local_vars

    def runControlCode(self, file_name, l, running):
        """runs the control code"""
        global lck
        lck = l
        log = self.log
        local_vars = locals()
        global_vars = self.extractLocals(globals(), self.orpd_server.listFunctions())
        plog = ProxyLogger(logging.getLogger('Control Code'))
        global_vars['log'] = plog
        global_vars['debug'] = plog.debug
        global_vars['info'] = plog.info
        global_vars['warning'] = plog.warning
        global_vars['error'] = plog.error
        global_vars['critical'] = plog.critical
        global_vars['registerCallback'] = self.mleq.registerCallback
        global_vars['setPriority'] = self.mleq.setPriority
        global_vars['handleEvents'] = self.handleEvents
        global_vars['triggerEvent'] = self.mleq.triggerEvent
        global_vars['stop'] = self.stopControlCode
        log.info('Control Code Started')
        threading.settrace(tracer)
        self.proc = threading.Thread(target=self.executeControlCode,
                        args=(file_name, global_vars, local_vars))
        self.proc.start()
        self.proc.join()
        self.running.value = False

    def stopControlCode(self):
        """Stops the control code"""
        timer = Timer(2, self._forceStop)
        timer.start()
        self.running.value = False
        self.evt_handler.join()
        timer.cancel()
        
    def _forceStop(self):
        """Called if stopControlCode Fails"""
        sys.exit(1)

    def startDeviceServices(self):
        """Starts Services specified by Devices"""
        if self.hardware_modules_services:
            sys.path.append(os.path.join(os.getcwd(), 'files'))
            for service in self.hardware_modules_services:
                try:
                    exec("import %s" % service[0])
                    if len(service) == 2:
                        exec('%s.%s.start()' % (service[0], service[1]))
                    elif len(service) == 3:
                        exec('%s.%s.start(*service[2])' % (service[0], service[1]))
                    elif len(service) == 4:
                        exec('%s.%s.start(*service[2], **service[3])' % (service[0], service[1]))
                except ImportError as error:
                    self.log.error('Hardware Module Service Error: Module %s does not exist' % service[0])
                except AttributeError as error:
                    self.log.error('Hardware Module Service Error: %s.%s is not a valid service' % (service[0], service[1]))
                except Exception as error:
                    logError(sys.exc_info(), self.log.error, 'Hardware Module Service Error:', importspecial.MAGIC_LINENO)
    
    def handleEvents(self):
        """Handles Events"""
        try:
            self.evt_handler = EventRetriever(self.running, self.queue, self.log, self.lock, self.mleq)
            self.evt_handler.start()
            while self.running.value:
                with self.lock:
                    evt = self.mleq.retrieveEvent()
                    if evt:
                        evt()
        except Exception as error:
            logError(sys.exc_info(), self.log.error, 'Error while Handling an Event:', importspecial.MAGIC_LINENO)
    
    def registerDeviceServices(self, devices):
        """Cycle through devices and register hardware services."""
        try:
            for device in devices:
                service_list = device.getServices()
                if service_list and len(service_list):
                    for service in service_list:
                      self.hardware_modules_services.append(service)
        except Exception as error:
            lgoError(sys.exc_info(), self.log.error, 'Sandbox HWM Services Error:', importspecial.MAGIC_LINENO)
    
    def addSubDirectories(self, path):
        """Function that adds all sub directories to the CC_PATH"""
        for root_path, _, _ in os.walk(path):
            importspecial.CC_PATH.append(root_path)
    
    def setupCCPath(self, path):
        """Configures the CC_PATH for importing special .cc files"""
        # Add cwd/files and sub directories
        self.addSubDirectories(os.path.join(path, 'files')) # Working Directory's cc folder
        self.addSubDirectories(os.path.join(path, 'modules')) # Working Directory's cc folder
        self.addSubDirectories(os.path.join(sys.path[0], 'files')) # ORP's builtin cc folder
        self.addSubDirectories(os.path.join(sys.path[0], 'modules')) # ORP's builtin cc folder
    
    def startUp(self, devices, path, file_name, lock, running, queue):
        """Preforms startup activities"""
        lib_dir = os.path.join(os.getcwd(), 'lib')
        os.chdir(path)
        sys.path.append(path)
        sys.path.append(lib_dir)
        
        # Setup the .cc path
        self.setupCCPath(path)
        
        # Register event queue
        self.queue = queue
        self.running = running
        self.running.value = True
        
        self.mleq = MultiLevelEventQueue(queue, lock)
        
        # Register the kill function
        signal.signal(signal.SIGINT, signalShutdown)
        
        # Connect to the Daemon's Log Server
        log = self.root_log = logging.getLogger('')
        log.setLevel(logging.DEBUG)
        log = self.log = logging.getLogger('Sandbox')
        log.setLevel(logging.DEBUG)
        
        # Connect to the orpd xmlrpc server
        self.orpd_server = xmlrpclib.Server('http://localhost:7003/')
        
        # Serve forevere
        log.debug('Sandbox Started')
        
        # Setup device services
        self.registerDeviceServices(devices)
        
        # Run the Control Code
        self.runControlCode(file_name, lock, running)
        
        # Exit Cleanly
        log.debug('Sandbox Stopped')
        sys.exit(0)
    