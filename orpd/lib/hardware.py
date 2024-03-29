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
hardware.py - Contains facilities for hardware modules

Created by William Woodall on 2010-10-14.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os
import traceback
import logging
import inspect
from threading import Thread, Lock, Event

from logerror import logError

import orpdaemon

###  Variables  ###
XMLRPCSERVER = None

###  Class  ###
class Device(object):
    """Device is the parent class to all hardware modules"""
    def __init__(self, config):
        "A basic device component, all other hardware inherit from this class"
        self.config = config
        self.name = config['name']
        self.log = logging.getLogger(self.name)
    
    def triggerEvent(self, name, data, obj_name=None):
        """Allows Control Code to trigger events"""
        split_name = name.split('.')
        if len(split_name) == 2:
            obj_name = split_name[0]
            name = split_name[1]
        else:
            if not obj_name:
                obj_name = self.name
        event = [obj_name, name, data]
        if XMLRPCSERVER != None and XMLRPCSERVER.sandbox_running != None and XMLRPCSERVER.sandbox_running.value:
            XMLRPCSERVER.sandbox_queue.put(event)
        else:
            self.log.debug("Event dropped because no CC handling events. Event \'%s\': %s" % (str(event[0]+'.'+event[1]), str(event[2]).strip()))
    
    def init(self):
        'Called when daemon starts'
        pass
    
    def start(self):
        "A callback for CC startup"
        pass
    
    def getServices(self):
        """A list of services the hardware module can start. 
            retrun Format:  [["<library>", "<function>", (args,), [kwargs]], ...]
        """
        pass
    
    def stop(self):
        "A callback for CC shutdown"
        pass
    
    def __str__(self):
        if self.name:
            return self.name + '.*'
    
    def __repr__(self):
        return self.__str__()
    

class SerialListener(Thread):
    """This is a facility for mapping callbacks to messages over serial
        
Specifically this can be used to register callback functions to 
specific messages from somthing like a serial port.

Attributes:
------------------
serial_port:    <serial.Serial> serial port object

listening:      <boolean> True if lestening, False otherwise

Functions:
------------------
addHandler(comparator, callback)->None
    Throws ValueError: on invalid arguments
     comparator is either True or a function. That function must return a 
     boolean value when passed the message in question.  callback is a 
     function that is called iff the comparator returns True and is also 
     passed the msg.
     
listen(clear=False)->None
   Throws Exception: will raise any serial errors that occur opening the port
    This causes the SerialListener to start listening, which means it will begin
    monitoring the serial_port for messages. The clear parameter if False will 
    process any existing data in the serial buffer, but if True it will clear the 
    serial data buffer before parsing the data.
        
stopListening()->None
    Throws Exception: will raise any seiral errors that occur
     Stops listening if you are listening.  Does nothing if you are not currently
     listening.

Examples:
------------------
#In this example isReset tests the incoming messages for the str 'RST'
#if it returns true then the resetReceived function is called and passed
#the msg.

def isReset(msg):
    if 'RST' in msg:
        return True
    return False

def resetReceived(msg):
    log.debug(self.name+' microcontroller reset: '+msg)

import serial
my_serial_obj = serial.Serial('/dev/ttyS0')
        
serial_listener = SerialListener(my_serial_obj, log)
serial_listener.addHandler(isReset, resetReceived)
serial_listener.listen()
        
#In this example every message is passed to one handler function.

def handler(msg):
    log.debug("From micro1 "+msg)

import serial
my_serial_obj = serial.Serial('/dev/ttyS0')

serial_listener = SerialListener(my_serial_obj, log)
serial_listener.addHandler(True, handler)
serial_listener.listen()
------------------
    """
    def __init__(self, serial_port=None, logger=None, delimiters=('\r','\n')):
        # Check the value of serial_port and see if it was passed
        Thread.__init__(self)
        if serial_port != None:
            self.serial_port = serial_port
        else:
            raise ValueError("You must pass a valid serial port for the first parameter")
	if logger != None:
            self.log = logger
        else:
            raise ValueError("You must pass a valid logger for the first parameter")
        self._running = True
        self._listening = False
        self._listening_lock = Lock()
        self._listening_event = Event()
        self.handlers = []
        self.delimiters = delimiters
        self._start()
        
    def __del__(self):
        self._listening_lock.acquire()
        self._listening = False
        self._listening_lock.release()
        self._running = False
        self._listening_event.set()
        
    def listen(self, clear=False):
        """Begins to listen to the serial port for messages
        
        Throws Exception: will raise any serial errors that occur opening the port
         This causes the SerialListener to start listening, which means it will begin
         monitoring the serial_port for messages. The clear parameter if False will 
         process any existing data in the serial buffer, but if True it will clear the 
         serial data buffer before parsing the data."""
        self._listening_lock.acquire()
        if self._listening:
            return
        else:
            self._listening = True
        self._listening_lock.release()
        # Clear buffer is necessary
        if clear and self.serial_port.isOpen():
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
        # Notify the thread to continue
        self._listening_event.set()
        
    def isListening(self):
        """Returns True if it is listening, False otherwise"""
        self._listening_lock.acquire()
        result = self._listening
        self._listening_lock.release()
        return result
        
    def stopListening(self):
        """Stops listening if you are
        
        Throws Exception: will raise any seiral errors that occur
         Stops listening if you are listening.  Does nothing if you are not currently
         listening."""
        self._listening_lock.acquire()
        self._listening = False
        self._listening_lock.release()
    
    def _start(self):
        """Internal shortcut to Thread's start method"""
        Thread.start(self)
    
    def start(self):
        """Overrides Thread's start method"""
        raise NotImplementedError("Use SerialListener.listen() to start the listener.")
        
    def _join(self, timeout=None):
        """Internal shortcut to Thread's join method"""
        Thread.join(self, timeout)
        
    def join(self, timeout=None):
        """Overrides Thread's join method"""
        self._listening_lock.acquire()
        self._listening = False
        self._listening_lock.release()
        self._running = False
        self._listening_event.set()
        self._join()
    
    def run(self):
        """Overrides Thread's run method"""
        try:
            serial = self.serial_port
            # Open the serial port if it isn't
            while self._running:
                try:
                    if not serial.isOpen():
                        serial.open()
                except Exception as error:
                    error.args = ("Error opening Serial Port, did you pass a serial port object and not a string?",)
                    raise error
                while True:
                    token = ''
                    message = ''
                    # Make sure we are still supposed to be listening
                    self._listening_lock.acquire()
                    temp_listening = self._listening
                    self._listening_lock.release()
                    if not temp_listening or not self._running:
                        break
                    # Read until you get a delimiter
                    while token not in self.delimiters:
                        token = serial.read()
                        message += token
                        self._listening_lock.acquire()
                        temp_listening = self._listening
                        self._listening_lock.release()
                        if not temp_listening or not self._running:
                            break
                    if not temp_listening or not self._running:
                        break
                    # We have gotten a delimiter now we need to 
                    # determine if there is a callback for this message
                    for comparator, callback in self.handlers:
                        callback_event = None
                        try:
                            if ((inspect.isfunction(comparator) or inspect.ismethod(comparator)) and comparator(message)) or \
                                                                            (isinstance(comparator, bool) and comparator):
                                callback_event = callback(message)
                        except Exception as err:
                            logError(sys.exc_info(), self.log.error, 'Exception handling serial message:', orpdaemon.HWM_MAGIC_LINENO)
            
                # Close everything after exiting the loop
                serial.close()
                # Wait for either __del__ or listen to be called again
                self._listening_event.wait()
                self._listening_event.clear()
        except Exception as err:
	    print 'fdsa'
            logError(sys.exc_info(), self.log.error, 'Exception in Serial Listener:', orpdaemon.HWM_MAGIC_LINENO)
        
    def addHandler(self, comparator, callback):
        """Adds a handler to the SerialListener
        
        Throws ValueError: on invalid arguments
         comparator is either True or a function. That function must return a 
         boolean value when passed the message in question.  callback is a 
         function that is called iff the comparator returns True and is also 
         passed the msg."""
        # Make sure that the comparator is either a function or a boolean
        if not (inspect.isfunction(comparator) or inspect.ismethod(comparator) or isinstance(comparator, bool)):
            raise ValueError("Invalid comparator passed to addHandler, must be a function or boolean")
        # If comparator is a function check to make sure it takes atleast 1 argument beyond self
        if inspect.isfunction(comparator) or inspect.ismethod(comparator):
            args = inspect.getargspec(comparator).args
            try:
                args.remove('self')
            except: pass
            if len(args) == 0:
                raise ValueError("Invalid comparator passed to addHandler, must take atleast one argument")
        # Make sure that the callback is a function
        if not (inspect.isfunction(callback) or inspect.ismethod(callback)):
            raise ValueError("Invalid callback passed to addHandler, must be a function")
        else:
            # Make sure it has atleast one argument for the msg
            args = inspect.getargspec(callback).args
            try:
                args.remove('self')
            except: pass
            if len(args) == 0:
                raise ValueError("Invalid callback passed to addHandler, must take atleast one argument")
        self.handlers.append((comparator, callback))

###  Functions  ###
def expose(func):
    """Decorator that exposes the function to the xmlrpc server"""
    func.exposed = True
    return func
