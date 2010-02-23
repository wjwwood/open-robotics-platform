#!/usr/bin/python -OO
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

"""Open Robotics Platform Daemon

This is the main script that starts all main functionality and daemonizes.
"""

__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import os       # OS interface
import sys      # System specific interface
import signal   # Library for handling posix signals
import getopt   # Command line argument parser
import logging  # Builtin logging facility for python
import logging.config
import ConfigParser # Config file system for python

### Persistent Variables
# I need these to persist information between server restarts
network_handlers = {}

###  Functions  ###

def usage():
    """Returns the usage information"""
    return """Open Robotics Platform Daemon - Usage:
\t-c, --config=\t\tThis allows you to specify a config file
\t-d, --daemonize\t\tThis daemonizes the process
\t-h, --help\t\tThis prints the usage message
\t-o, --output=\t\tThis should be followed by desired log file
\t-w, --work-directory=\tThis sets the working directory"""

def handleCommandArguments(arguments):
    """docstring for handleCommandArguments"""
    # Parse arguments
    short_opts = "hvdo:w:c:"
    long_opts = ['help', 'verbose', 'daemonize', 'output=', 'work-directory=', 'config=']
    try:
        opts, args = getopt.getopt(arguments[1:], short_opts, long_opts)
    except getopt.GetoptError as error:
        print str(error)
        print usage()
        sys.exit(2)
    # Initialize variables
    result = {}
    result['daemonize'] = False
    result['verbose'] = False
    result['output_file_name'] = None
    result['work_directory'] = None
    result['config_file_name'] = None
    # Handle opts and args
    for opt, arg in opts:
        # If help
        if opt in ('-c', '--config='):
            result['config_file_name'] = a
        if opt in ('-h', '--help'):
            print usage()
            sys.exit(0)
        if opt in ('-v', '--verbose'):
            result['verbose'] = True
        if opt in ('-d', '--daemonize'):
            result['daemonize'] = True
        if opt in ('-o', '--output='):
            result['output_file_name'] = arg
        if opt in ('-w', '--work-directory='):
            result['work_directory'] = arg
    # Return the arguments
    return result


def loadDefaultLogger():
    """Loads the default minimal logger, only used
    when no config file is found."""
    from logging import StreamHandler, Formatter, getLogger, INFO, DEBUG
    # Setup console logger
    console = StreamHandler(sys.stdout)
    # Setup Formatter
    formatter = Formatter('%(name)-8s: %(levelname)-12s %(message)s')
    console.setFormatter(formatter)
    console.setLevel(INFO)
    # Get the root loger and add the handlers
    root = getLogger('')
    root.addHandler(console)
    root.setLevel(DEBUG)
    # Set the logger
    return getLogger('ORPD')

def startLogging():
    """Initializes logging"""
    # Try to load the normal logging config file
    try:
        if os.path.exists('config/logging.cfg'):
            logging.config.fileConfig('config/logging.cfg')
        else:
            logging.config.fileConfig('config/logging.cfg.default')
        log = logging.getLogger('ORPD')
    except ConfigParser.NoSectionError as error:
        # No config files, load defaults
        log = loadDefaultLogger()
        log.debug('Exception loading logging config, Using default logging settings')
    log.debug('Logger Started')

def startup(argv=sys.argv):
    """This is the main function that creates objects and starts the server"""
    configs = handleCommandArguments(argv)
    startLogging()
    # Create and start the Daemon
    from lib.orpdaemon import ORPDaemon
    orpd = ORPDaemon(work_directory=configs['work_directory'], config_file_name=configs['config_file_name'])
    running = True
    while running:
        # Register the shutdown signal
        signal.signal(signal.SIGINT, orpd.shutdown)
        # Start the server
        work_dir = orpd.startRPCServer()
        if work_dir != None:
            orpd = ORPDaemon(work_directory=work_dir)
        else:
            running = False
    orpd.log.info('Stopping the server...')
    orpd.logging_server.shutdown()

###  If Main  ###

if __name__ == '__main__':
    startup(sys.argv)
