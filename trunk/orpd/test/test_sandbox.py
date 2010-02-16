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
test_sandbox.py - Tests related to spawning and controlling the sandbox.

Created by William Woodall on 2009-09-29.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os
import unittest

import test_helper
from time import sleep
from nose.plugins.skip import SkipTest

###  Class  ###
class ORPDSandboxTestCases(unittest.TestCase):
    """Test cases for sandbox related functionality"""
    def setUp(self):
        """Ran before each test"""
        self.proc, self.server = test_helper.startServerIfStopped()
        
    def test_SpawnSandbox(self):
        """Spawning, testing, and shutting down sandbox"""
        raise SkipTest
        # Spawn the sandbox
        self.assertTrue(self.server.runControlCode('shutdown.cc'), "Sandbox did not start")
        # Shutdown the Sandbox
        self.assertTrue(self.server.stopControlCode(), "There was a problem killing the sandbox")
    
    def test_object_instances(self):
        raise SkipTest
        # Spawn the sandbox
        sleep(1)
        self.assertTrue(self.server.runControlCode('test_foosensor.cc'), "Sandbox did not start")
        # sleep(1)
        # Check to make sure if it is still running (didn't die immediately)
        self.assertTrue(self.server.controlCodeRunning(), "Sandbox died immediately")
        # sleep(1)
        # Shutdown the Sandbox
        self.assertTrue(self.server.killControlCode(), "There was a problem killing the sandbox")
        # sleep(1)

        
    def tearDown(self):
        """Ran after each test"""
        pass
        

###  Functions  ###


###  IfMain  ###

if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        test_helper.stopServer()

