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
servies.py - This module allows for easy, safe threading in control code.

The @service decorator is included in control code file by default.
"""
__author__ = "John Harrison"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###
import sys
import traceback
import re
import logging
import threading

# Setup logging
log = logging.getLogger('ORPD')

from lib import importspecial

def logError(exc_info, log_func, msg, line_no_delta=0):
    """Logs an error with a traceback"""
    exceptionType, exceptionValue, exceptionTraceback = exc_info
    tb_list = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
    tb_message = ''.join(tb_list)
    match = re.search(r'(.*)line\s(\d*)(.*)', tb_message, re.M | re.S)
    tb_message = match.group(1) + 'line ' + str(int(match.group(2)) - line_no_delta) + match.group(3)
    log_func(msg+'\n'+tb_message)

class Service(object):
    """This class facilatates safe threading in control code"""
    def __call__(self, *args, **kwargs):
        return self.start(*args, **kwargs)
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.running = False
    
    def __go(self):
        while self.running:
            try:
                self.func(*self.args, **self.kwargs)
            except Exception as exception:
                self.stop()
                logError(sys.exc_info(), log.error, 'Control Code Service Error:', importspecial.MAGIC_LINENO)
    
    def start(self, *args, **kwargs):
        self.running = True
        if args:
            self.args = args
        if kwargs:
            self.kwargs = kwargs
        self.proc = threading.Thread(target=self.__go)
        self.proc.start()
    
    def toggle(self, *args, **kwargs):
        if self.running:
            self.running = False
        else:
            return self.start(*args, **kwargs)
    
    def stop(self):
        self.running = False
    

def service(func, *args, **kwargs):
    """This is a decorator that provides safe threading in control code
        
    This can be used to loop a function indefinately which can be 
    started and stopped at any point.  
        
    Example control code which will print 'hi' every 10 seconds:
    @service
    def foo():
        log.info('hi')
        sleep(10)
        
    def main():
        foo() # or foo.start() and to stop it foo.stop()
        handleEvents()
    """
    result = Service(func, *args, **kwargs)
    return result