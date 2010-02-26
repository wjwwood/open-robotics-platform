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
remotecontrol.py - Contains the functionality of the remote control system

Created by William Woodall on 2010-11-13.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import os.path
import wx
import threading
import lib.elements as elements

###  Variables  ###
process = None

###  Functions  ###

### Constants ###
# Sensitivity affects how significant a change in joystick position has
# to be in order for it to register as a movement.
SENSITIVITY = 5
INVERT_SPEED = True
INVERT_DIRECTION = False
# Dead Zone is the range around 0 that will be ignored to prevent jittering
# when centering the joystick
DEAD_ZONE = [127, 128]
DEAD_ZONE_2 = 0.25
# Network Throttle indicates how long to wait between each transmission
# over the network.  Use this to reduce congestion on slow connections.
# In seconds, I recommend no more than .01 or 10 ms.
THROTTLE = 0.0

ps3 = None

class PS3(object):
    def __init__(self):
        self.speed = 0
        self.direction = 0
        self.running = True
        self.event = threading.Event()
    def convert(self, num):
        result = (num - 127.0) / 127.0
        if result > 1:
            result = 1
        if result < -1:
            result = -1
        return result
    def printSD(self):
        from time import sleep
        while self.running:
            # sleep(THROTTLE)
            self.event.wait(0.5)
            asdf = self.event.isSet()
            if asdf:
                if self.speed in DEAD_ZONE:
                    self.speed = 127
                if self.direction in DEAD_ZONE:
                    self.direction = 127
                speed = self.convert(self.speed)
                direction = self.convert(self.direction)
                if abs(speed) < DEAD_ZONE_2:
                    speed = 0
                if INVERT_SPEED:
                    speed *= -1
                if abs(direction) < DEAD_ZONE_2:
                    direction = 0
                if INVERT_DIRECTION:
                    direction *= -1
                ## useful for debugging
                # print 'speed:', speed, 'direction:', direction
                try:
                    elements.REMOTE_SERVER.mc.move(speed/8.0, direction/8.0)
                except:
                    pass
            self.event.clear()
                
    def stop(self):
        self.running = False
        
    def start(self):
        self.running = True
        
    def onJoyMove(self, event):
        point = event.GetPosition()
        x = point.x
        y = point.y
        go = False
        if abs(self.speed - y) > SENSITIVITY:
            self.speed = y
            go = True
        if abs(self.direction - x) > SENSITIVITY:
            self.direction = x
            go = True
        if go:
            self.event.set()

def toggle(event=None):
    """Toggles the system on and off"""
    global ps3
    if ps3 == None:
        ps3 = PS3()
        if not getattr(elements.MAIN, 'joy', False):
            elements.MAIN.joy = wx.Joystick()
        elements.MAIN.Bind(wx.EVT_JOY_MOVE, ps3.onJoyMove)
        elements.MAIN.joy.SetCapture(elements.MAIN)
        PS3.handler = threading.Timer(0.5, ps3.printSD)
        PS3.handler.start()
        ps3.start()
        elements.TOOLBAR.RC_button.SetLabel('Turn off R/C')
    else:
        ps3.stop()
        PS3.handler.join()
        elements.MAIN.joy.ReleaseCapture()
        # elements.MAIN.Unbind(wx.EVT_JOY_MOVE, ps3.onJoyMove)
        elements.TOOLBAR.RC_button.SetLabel('Turn on R/C')
        ps3 = None

