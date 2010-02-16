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
__init__.py - Starts and manages logging in the dashboard

Created by William Woodall on 2009-11-05.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os
import logging
import thread

# Other Libraries
import lib.elements as elements
from lib.log.network import NetworkEventHandler
from lib.log.sockethandler import LogRecordSocketReceiver
from lib.events.log import EVT_LOGRX
from lib.events.log import logReceived

###  Functions  ###

def start():
    """Configures all logging related functions and returns the logger"""
    log = logging.getLogger('Dashboard')
    log_root = logging.getLogger('')
    # Bind the receiving of a log to update the console
    elements.MAIN.Bind(EVT_LOGRX, logReceived)
    
    # Setup Log event handling
    NetworkEventHandler.win_id = elements.MAIN.id
    NetworkEventHandler.handler = elements.MAIN.GetEventHandler()
    
    # Setup the network logging
    elements.NETWORK_LOG_SERVER = LogRecordSocketReceiver()
    event_handler = NetworkEventHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)-20s -\
            %(levelname)-12s - %(message)s\n")
    event_handler.setFormatter(formatter)
    log_root.addHandler(event_handler)
    thread.start_new_thread(elements.NETWORK_LOG_SERVER.serve_until_stopped, ())
    
    return log
