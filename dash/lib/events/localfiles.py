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
localfiles.py - Contains handlers related to local file actions

Created by William Woodall on 2010-10-30.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os
import logging
import thread

# Other Libraries
import lib.elements as elements

try: # try to catch any missing dependancies
# wx for window elements
    PKGNAME = 'wxpython'
    import wx
    import wx.aui as aui
    import wx.lib.agw.genericmessagedialog as GMD

    del PKGNAME
except ImportError as PKG_ERROR: # We are missing something, let them know...
    sys.stderr.write(str(PKG_ERROR)+"\nYou might not have the "+PKGNAME+" \
            module, try 'easy_install "+PKGNAME+"', else consult google.")

# Setup logging
log = logging.getLogger('Dashboard')

###  Functions  ###

def saveFile(event):
    """This function saves the currently selected file"""
    editor = elements.MAIN.GetActiveChild()
    contents = editor.text_ctrl.GetText()
    path = editor.path
    
    # Check to see if this is a config file
    if editor.file_type == 'config':
        elements.REMOTE_SERVER.sendConfig(contents)
        log.info('Config File Sent')
        dlg = GMD.GenericMessageDialog(elements.MAIN, 
        "After editing the config files you must restart the robot.  Do you wish to do that now?",
        "Restart the Robot?",
        wx.ICON_QUESTION | wx.YES_NO)
        dlg.ShowModal()
        ret_code = dlg.GetReturnCode()
        if ret_code == 5103: # Yes was selected
            elements.REMOTE_SERVER.restart()
        elif ret_code == 5104: # No was selected
            pass
        else:
            raise Exception('Dialog return code was invalid!')
        return
    
    # Check to see if it is an untitled document
    if editor.path == None:
        dlg = wx.FileDialog(elements.MAIN, "Choose a file", os.path.join(os.getcwd(), 'files'), "", "*.*", \
                            wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() != wx.ID_OK:
            return
        filename = dlg.GetFilename()
        dirname = dlg.GetDirectory()
        path = os.path.join(dirname, filename)
    else:
        # Else just split the path
        dirname, filename = os.path.split(path)
    
    tmp_file = open(path, 'w+')
    tmp_file.write(contents)
    tmp_file.close()
    
    relative_path = path.replace(os.getcwd(), '')[1:]

    try:
        elements.REMOTE_SERVER.write(relative_path, contents, os.stat(path)[8])
    except Exception as e:
        pass
    
    # Update the project drawer
    elements.PROJECT_DRAWER.updateList()
    
    # Update the Tab label
    editor.SetTitle(filename)
    editor.path = path
    
    log.info('File %s saved' % filename)
    
def runLocally(event):
    """Runs the currently selected file in the local terminal"""
    contents = elements.MAIN.GetActiveChild().text_ctrl.GetText()
    for line in contents.splitlines():
        if line.isspace() == False:
            thread.start_new_thread(elements.INTERACTIVE_CONSOLE.run, (line,), {'prompt':False, 'verbose':True})
    