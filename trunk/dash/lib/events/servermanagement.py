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
servermanagement.py - Contains components related to remote server management

Created by William Woodall on 2009-11-03.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os
import logging
import thread
import xmlrpclib
import copy
import traceback

# Other libraries
import lib.elements as elements

try: # try to catch any missing dependancies
# wx for window elements
    PKGNAME = 'wxpython'
    import wx
    import wx.aui as aui

    del PKGNAME
except ImportError as PKG_ERROR: # We are missing something, let them know...
    sys.stderr.write(str(PKG_ERROR)+"\nYou might not have the "+PKGNAME+" \
module, try 'easy_install "+PKGNAME+"', else consult google.")

###  Functions  ###

def sync_files(files):
    cc_files, hwm_files = files
    # print "CC Files: ", cc_files
    # print "HWM Files: ", hwm_files
    sync_files_helper(cc_files, "files", elements.MAIN.files[0])
    sync_files_helper(hwm_files, "modules", elements.MAIN.files[1])
    elements.MAIN.buildListing()
    elements.MAIN.project_drawer.updateList()
    
    
def sync_files_helper(files, root_folder, base_array):
    local_array = copy.deepcopy(base_array)
    for file in files:
        try:
            path_array = file.split('/')
            parent_array = file_array = local_array
            file_index_reference = None
            try:
                if len(path_array):
                    for x in path_array:
                        parent_array = file_array
                        file_array = file_array[x]
                        file_index_reference = x
            except KeyError as filename_error:
                pass
            if file_array[1] == files[file]:
                # Same file
                # print 'same file'
                pass
            elif file_array[1] > files[file]:
                # Local copy is newer
                # print 'local copy newer for: ', file
                contents = open(file_array[0], 'r').read()
                elements.REMOTE_SERVER.write(root_folder + '/' + file, contents, file_array[1])
            elif file_array[1] < files[file]:
                # Server Copy is newer
                # print 'server copy newer for: ', file
                file_path = os.path.join(os.getcwd(), root_folder, file)
                with open(file_path, 'w+') as fp:
                    fp.write(elements.REMOTE_SERVER.getFileContents(root_folder + '/' + file))
                os.utime(file_path, (files[file], files[file]))
            del parent_array[file_index_reference]
        except KeyError:
            try:
                if file.find('/') != -1:
                    os.makedirs(os.path.join(os.getcwd(), root_folder, os.path.split(file)[0]))
                file_path = os.path.join(os.getcwd(), root_folder, file)
                with open(file_path, 'w+') as fp:
                    fp.write(elements.REMOTE_SERVER.getFileContents(root_folder + '/' + file))
                os.utime(file_path, (files[file], files[file]))
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                print "Report this bug."
                
    walk_and_send_files(root_folder, local_array)

def walk_and_send_files(root, list):
    """Walks a hash and sends the files to the remote server."""
    if isinstance(list, dict):
        for file in list:
            new_root = root + '/' + file
            walk_and_send_files(new_root, list[file])
    else:
        file_handler = open(list[0], 'r')
        elements.REMOTE_SERVER.write(root, file_handler.read(), list[1])
    
def connect(event):
    """Connects to the remote server, using the info in remote server text box"""
    # Connect to the remote server
    location = elements.TOOLBAR.server_addr.GetValue()
    try:
        elements.REMOTE_SERVER = xmlrpclib.Server('http://' + str(location) + ':7003/')
        sync_files(elements.REMOTE_SERVER.connect())
        elements.TOOLBAR.connect_button.SetLabel('Disconnect')
        elements.TOOLBAR.connect_button.Bind(wx.EVT_BUTTON, disconnect)
        elements.MAIN.SetStatusText('Connected')
    except Exception as error:
        elements.MAIN.log.error(str(error))
        return
    
    # Activate Buttons
    elements.TOOLBAR.send_button.Enable()
    elements.TOOLBAR.config_button.Enable()
    elements.TOOLBAR.run_button.Enable()
    elements.TOOLBAR.shutdown_button.Enable()
    elements.TOOLBAR.restart_button.Enable()
    elements.TOOLBAR.RC_button.Enable()

def disconnect(event):
    """Attempts to disconnect from the remote server"""
    elements.TOOLBAR.connect_button.SetLabel('Connect')
    elements.TOOLBAR.send_button.Disable()
    elements.TOOLBAR.run_button.Disable()
    elements.TOOLBAR.shutdown_button.Disable()
    elements.TOOLBAR.restart_button.Disable()
    
    elements.TOOLBAR.connect_button.Bind(wx.EVT_BUTTON, connect)
    elements.REMOTE_SERVER.disconnect()
    elements.REMOTE_SERVER.remote_server = None
    elements.MAIN.SetStatusText('Disconnected')

def restart(event):
    """Calls the remote server to restart"""
    elements.REMOTE_SERVER.restart()
    
def shutdown(event):
    """Shuts down the remote server"""
    elements.REMOTE_SERVER.shutdown()
    disconnect(None)