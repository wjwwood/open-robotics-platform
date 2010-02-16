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
orpdaemon.py - ORPDaemon class, contains the class which encapsulates all 
of the data and code related to the orp daemon

Created by William Woodall on 2009-10-13.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os
import select
import logging
import logging.config
import thread
import inspect
import ctypes
import tempfile
import imp
from multiprocessing import Value

# Import ORP Modules
import hardware
from loggingserver import LogRecordSocketReceiver
from rpcserver import RPCServer

try: # try to catch any missing dependancies
# YAML for configuration files
    PKGNAME = 'pyyaml'
    import yaml

    del PKGNAME
except ImportError as PKG_ERROR: # We are missing something, let them know...
    sys.stderr.write(str(PKG_ERROR)+"\nYou might not have the "+PKGNAME+" \
module, try 'easy_install "+PKGNAME+"', else consult google.")

###  Class  ###

class ORPDaemon(object):
    """ORPDaemon class is a singlton class"""
    def __init__(self, work_directory = None, config_file_name = None, port = None):
        # Initialize variables
        self.logging_server = None
        self.xml_server = None
        self.port = None
        self.log = None
        self.config = None
        self.config_file_name = None
        self.work_directory = None
        self.new_work_dir = None
        self.device_objects = []
        # Load logging
        self.startLogging()
        
        # Set work directory
        self.setupWorkingDirectory(work_directory)
        
        # Load Configs
        self.loadConfigs(config_file_name)
        self.log.info('Using work directory: '+os.getcwd())
        
        # Setup xmlrpc server
        if port != None:
            self.port = port
        else:
            try:
                self.port = self.config['port']
            except KeyError:
                self.port = 7003
        # Create the RPC Server
        self.xml_server = RPCServer(('', self.port), self)
        # Enables Introspection, part of the SimpleXMLRPCServer Class
        self.xml_server.register_introspection_functions()
        # Set the xml_server in the hardware library
        hardware.XMLRPCSERVER = self.xml_server
        
        # Create hardware objects from configs
        self.createObjects()
        
        # Notify that the server is ready
        self.log.info('Server Ready')

    def startLogging(self):
        """Setups the logger for the daemon and a logging server"""
        # Setup the logger for this daemon
        self.log = logging.getLogger('ORPD')
        # Setup a network logging server
        self.logging_server = LogRecordSocketReceiver(port=7006)
        thread.start_new_thread(self.logging_server.serve_until_stopped, ())

    def setupWorkingDirectory(self, wk_directory = None):
        """Setups the working directory"""
        work_directory = self.work_directory = wk_directory
        # See if work_directory is none
        if work_directory == None:
            # Else make it the directory of execution
            self.setupWorkingDirectory(os.getcwd())
            return
        # Make sure the directory exists
        if not os.path.exists(work_directory):
            self.log.warning('Work directory specified does not exist:\n\t\t\t'\
                                                                +work_directory)
            self.setupWorkingDirectory()
            return
        # Now we have a working directory that exists set it
        os.chdir(work_directory)
    
    def loadConfigs(self, config_file_name = None):
        """Loads the config Files"""
        # Check if config_file_name is None
        if config_file_name == None:
            config_file_name = 'config/orpd.cfg'
        try:
            config = yaml.load(file(config_file_name, 'r'))
        except IOError:
            self.log.info('\'%s\' not present looking for orpd.cfg.default' 
                                                        % config_file_name)
            try:
                config_file_name += '.default'
                config = yaml.load(file(config_file_name, 'r'))
            except IOError:
                self.log.critical('No config files found, quitting...')
                raise IOError("No config files found!")
        # Made it through the try's
        self.config_file_name = config_file_name
        self.config = config
    
    def importHardwareModule(self, module_name, name):
        """Checks, mangles, and imports the HW module, returns the classes"""
        # Import the module
        f = open('modules/'+module_name+'.hwm', 'r')
        fp = tempfile.TemporaryFile()
        # No import required magic
        magic = \
"""
from lib.hardware import Device, expose
import logging
log = logging.getLogger(%s)
debug = log.debug
info = log.info
warning = log.warning
error = log.error
critical = log.critical
""" % ('\"'+name+'\"')
        fp.write(magic)
        # Append the hwm
        fp.write(f.read())
        # Don't forget to rewind! (this is necessary)
        fp.seek(0)
        # Now use imp magic to import the module
        try:
            hwmodule = imp.load_module(module_name, fp, 'modules/'+module_name+'.hwm', ('.hwm', 'r', imp.PY_SOURCE))
        except Exception as err:
            self.log.error('Error importing the module %s\n\t\t\t%s' % (name, str(err)))
            return None
        # The class should now be in the local dict
        for attr in dir(hwmodule):
            attribute = getattr(hwmodule, attr)
            if inspect.isclass(attribute):
                target_name = attribute.__name__.lower()
                target_name = target_name.replace('_', '-')
                if target_name != 'Device' and target_name == module_name:
                    return attribute
    
    def createObject(self, name, config):
        """Trys to create an object with the given configs"""
        try:
            # Only continue if the device is enabled
            enabled = config['enabled']
            if type(enabled) == bool and enabled:
                # Try to import the hardware module
                device_class = self.importHardwareModule(config['module'], config['name'])
                if device_class == None:
                    self.log.error('No proper class found for %s\n\t\t\t' % name+
                                    'The class name should be the same as the module, '+ \
                                    'camel case, and converting - to _')
                    return
                # Create the object
                try:
                    exec(config['name']+" = device_class(config)")
                    try:
                        exec("device_class.init("+config['name']+")")
                    except Exception as err:
                        self.log.warning('Error initializing %s:\n\t\t\t%s' % (device_class.__name__, str(err)))
                    # Add the object to the list of device objects
                    exec("self.device_objects.append(%s)" % config['name'])
                except Exception as error:
                    self.log.error("Error creating device %s:\n\t\t\t%s" % (name,str(error)))
            else:
                self.log.warning("Device %s is disabled, skipping..." % name)
        except KeyError as error:
            self.log.error("Manditory config '"+error.args[0]+\
                           "' not found for device '"+name+"'")
            self.log.error("Device %s will be disabled..." % name)
            
    def createObjects(self):
        """Creates objects based on config files and hardware modules"""
        # Parse config
        devices = self.config['Devices']
        for device in devices:
            self.createObject(device, devices[device])
        # Register the device isntances with the server
        for device_object in self.device_objects:
            self.exposeDeviceFunctions(device_object)
        
    def exposeDeviceFunctions(self, device_object):
        """
        Looks at the device object and expose the 
        methods that need to be exposed
        """
        function_list = {}
        for attr in dir(device_object):
            attribute = getattr(device_object, attr)
            if inspect.ismethod(attribute) and getattr(attribute, 'exposed', False):
                func = device_object.name+'.'+attribute.__name__
                function_list[func] = attribute
        self.xml_server.registerFunctions(function_list)
    
    def startRPCServer(self):
        """Starts the XMLRPC Server"""
        self.new_work_dir = None
        try:
            self.xml_server.serve_forever()
        except select.error:
            pass
        self.logging_server.shutdown()
        if self.new_work_dir != None:
            if os.path.exists(self.new_work_dir):
                return self.new_work_dir
        return None
    
    def shutdown(self, signal, frame):
        """Shuts down everything"""
        if signal and frame: # So pyCheckMate will shutup
            pass
        self.log.info('Caught Keyboard Interrupt')
        thread.start_new_thread(self.xml_server.shutdown, ())
    