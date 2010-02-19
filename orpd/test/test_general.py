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
test_general.py - Contains general test cases for the Robot Daemon

Created by William Woodall on 2010-09-22.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import unittest
import time
import os
from subprocess import Popen
import xmlrpclib as rpc
import test_helper

try: # try to catch any missing dependancies
# <PKG> for <PURPOSE>
    PKGNAME = '<EASY_INSTALL NAME>'
    # import <LIBRARY NAME>

    del PKGNAME
except ImportError as e: # We are missing something, let them know...
    sys.stderr.write("You might not have the "+PKGNAME+" module, \
                try 'easy_install "+PKGNAME+"', else consult google.\n"+e)

###  Class  ###
class ORPDGeneralTestCases(unittest.TestCase):
    """Test case for the ORPD"""
    def setUp(self):
        """Setup for tests"""
        self.proc, self.server = test_helper.startServerIfStopped()
    
    def test11_SyncFunction(self):
        """Trys the sync connection out"""
        self.assertEqual(self.server.ping(), True, "The ping function \
                                    return something other than True")
    
    def test99_Shutdown(self):
        """Tests the shutdown Command"""
        ret_code = test_helper.stopServer()
        self.failIfEqual(ret_code, None, "The Daemon has not \
                        shutdown after 10 seconds, failing and killing.")
        self.assertEqual(ret_code, 0, "The Daemon exited, but \
                        the return code was not zero, so an error occured.")
        
    def tearDown(self):
        """Cleanup"""
        pass

###  Functions  ###


###  IfMain  ###

if __name__ == '__main__':
    unittest.main()