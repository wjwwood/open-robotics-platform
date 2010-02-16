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
test_logging.py - Tests the logging capabilities of the server!

Created by William Woodall on 2009-09-24.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os
import unittest
import SocketServer
import logging.handlers
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
class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return cPickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)



class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """simple TCP socket-based logging receiver suitable for testing"""
    allow_reuse_address = 1
    def __init__(self, host='',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 5
        self.logname = None
        from threading import Lock
        self.lock = Lock()

    def serve_until_stopped(self):
        """docstring"""
        self.lock.acquire()
        import select
        rd, wr, ex = select.select([self.socket.fileno()],
                                   [], [],
                                   self.timeout)
        if rd:
            self.result = True
        else:
            self.result = False
        self.lock.release()

    def serveUntilStopped(self):
        """docstring for serve_until_stopped"""
        import thread
        thread.start_new_thread(self.serve_until_stopped, ())
        
    def getResult(self):
        """docstring for getResult"""
        self.lock.acquire()
        result = self.result
        self.lock.release()
        return result

class ORPDLoggingTestCases(unittest.TestCase):
    """Test case for the ORPD"""
    def setUp(self):
        """Setup for tests"""
        self.proc, self.server = test_helper.startServerIfStopped()
    
    def test10_TestXMLRPCLogging(self):
        """Tests the posting of logs to the daemon 
        through the xmlrpc interface"""
        self.server.info("Info Message")
        self.server.debug("Debug Message")
        self.server.warning("Warning Message")
        self.server.error("Error Message")
        self.server.critical("Critical Message")
    
    def test00_NetworkLogging(self):
        """Trys to connect to and get logging messages"""
        logserver = LogRecordSocketReceiver()
        logserver.serveUntilStopped()
        import time
        time.sleep(1)
        self.server.connect()
        self.server.info("Testing network logging")
        self.assertTrue(logserver.getResult())
        del logserver
                
    def tearDown(self):
        """Cleanup"""
        pass

###  Functions  ###


###  IfMain  ###

if __name__ == '__main__':
    unittest.main()