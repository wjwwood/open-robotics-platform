#!/usr/bin/env python -OO
# encoding: utf-8

###########
# ORP - Open Robotics Platform
#
# Copyright (c) 2009 John Harrison, William Woodall
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

Created by William Woodall on 2009-09-29.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

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
# from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Timer
from event_system import Event, MultiLevelEventQueue

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
    
def logError(exc_info, log_func, msg, line_no_delta=0):
    """Logs an error with a traceback"""
    exceptionType, exceptionValue, exceptionTraceback = exc_info
    print exceptionTraceback.tb_lineno
    tb_list = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
    tb_message = ''.join(tb_list)
    match = re.search(r'(.*)line\s(\d*)(.*)', tb_message, re.M | re.S)
    tb_message = match.group(1) + 'line ' + str(int(match.group(2)) - line_no_delta) + match.group(3)
    log_func(msg+'\n'+tb_message)

###  Classes  ###
class Proxy(object):
    pass

class EventRetriever(threading.Thread):
    """A thread that simply gets the events from the shared queue and 
    formats them a bit. It's simply a producer thread."""
    def __init__ (self, running, queue, callbacks, log, lock, mleq):
        ""
        threading.Thread.__init__(self)
        self.running = running
        self.queue = queue
        self.callbacks = callbacks
        self.log = log
        self.lock = lock
        self.mleq = mleq

    def run(self):
        """Overrides the run funtion in Thread"""
        while self.running.value:
            evt = self.queue.get(1)
            with self.lock:
                self.mleq.addEvent(Event(evt[0], vt[1], evt[2], self.callbacks, self.log))

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
        self.mleq = MultiLevelEventQueue()
        self.lock = threading.Lock()

    def __go(self, file_name, glbls, lcls):
        """Function to facilitate execution of control code"""
        fp = None
        try:
            import tempfile
            f = open(file_name, 'r')
            fp = tempfile.TemporaryFile()
            # No import required magic
            magic = """
from lib.services import service

import logging
log = logging.getLogger("ControlCode")
debug = log.debug
info = log.info
warning = log.warning
error = log.error
critical = log.critical
"""
            fp.write(magic)
            # Append the hwm
            fp.write(f.read())
            # Don't forget to rewind! (this is necessary)
            fp.seek(0)
            # Now use imp magic to import the module
            pathname, module_name = os.path.split(file_name)
            
            cc = imp.load_module(module_name[:-3], fp, pathname, ('.cc', 'r', imp.PY_SOURCE))
            for name, ptr in glbls.items():
                setattr(cc, name, ptr)
            self.startDeviceServices()
            cc.main()
        except Exception as error:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            tb_list = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
            tb_message = ''
            for line in tb_list:
                tb_message += line
            self.log.error('Control Code Error:\n\t'+tb_message)
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()
        

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
        global_vars['log'] = log
        global_vars['registerCallback'] = self.registerCallback
        global_vars['handleEvents'] = self.handleEvents
        global_vars['triggerEvent'] = self.triggerEvent
        global_vars['stop'] = self.stopControlCode
        log.info('Starting Control Code Execution')
        threading.settrace(tracer)
        self.proc = threading.Thread(target=self.__go,
                        args=(file_name, global_vars, local_vars))
        self.proc.start()
        self.proc.join()
        self.running.value = False
        log.info('Control Code Exiting...')

    def stopControlCode(self):
        """Stops the control code"""
        self.running.value = False
        self.evt_handler.join()

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
                    logError(sys.exc_info(), self.log.error, 'Hardware Module Service Error:')

    def handleEvents(self):
        """Handles Events"""
        try:
            self.evt_handler = EventRetriever(self.running, self.queue, self.callbacks, self.log, self.lock, self.mleq)
            self.evt_handler.start()
            while self.running.value:
                with self.lock:
                    evt = self.mleq.retrieveEvent()
                    if evt:
                        evt()
        except Exception as error:
            logError(sys.exc_info(), self.log.error, 'Error while Handling an Event:', 10)

    def registerDeviceServices(self, devices):
        """Cycle through devices and register hardware services."""
        try:
            for device in devices:
                service_list = device.getServices()
                if service_list and len(service_list):
                    for service in service_list:
                      self.hardware_modules_services.append(service)
        except Exception as error:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            tb_list = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
            tb_message = ''
            for line in tb_list:
                tb_message += line
            self.log.error('Sandbox HWM Services Error:\n'+tb_message)

    def startUp(self, devices, path, file_name, lock, running, queue):
        """Preforms startup activities"""
        lib_dir = os.path.join(os.getcwd(), 'lib')
        os.chdir(path)
        sys.path.append(path)
        sys.path.append(lib_dir)

        # Register event queue
        self.queue = queue
        self.running = running
        self.running.value = True

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
        log.info('Sandbox Starting...')

        # Setup device services
        self.registerDeviceServices(devices)

        # Run the Control Code
        self.runControlCode(file_name, lock, running)
        
        # Exit Cleanly
        sys.exit(0)
