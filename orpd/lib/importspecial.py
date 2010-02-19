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
importspecial.py - Importing this module will override the builtin __import__ 
funtion.  This allows us to use the import <module> method to import non .py 
files and gives us a chance to inject some 'Magic' into the cc files. 

Created by William Woodall on 2010-02-17.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import os
import sys
import imp
import logging
import tempfile
import re
import traceback

# Setup logging
log = logging.getLogger('ORPD')

# PATH for .cc files
CC_PATH = []
CC_PATH.append(os.getcwd())

# Magic to be added
# NOTE: If you edit this you need to change the MAGIC_LINE_NUMS
#        to match the number of Lines added to the .cc files 
#        otherwise the line numbers in errors will be incorrect

MAGIC = """
from lib.services import service
import logging
log = logging.getLogger("Control Code")
debug = log.debug
info = log.info
warning = log.warning
error = log.error
critical = log.critical
"""
MAGIC_LINE_NUMS = len(MAGIC.split('\n')) - 1

# Save the old __import__ reference
BUILTIN_IMPORT = __builtins__["__import__"]

###  Functions  ###

def logError(exc_info, log_func, msg, line_no_delta=0):
    """Logs an error with a traceback"""
    exceptionType, exceptionValue, exceptionTraceback = exc_info
    tb_list = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
    tb_message = ''.join(tb_list)
    match = re.search(r'(.*)line\s(\d*)(.*)', tb_message, re.M | re.S)
    tb_message = match.group(1) + 'line ' + str(int(match.group(2)) - line_no_delta) + match.group(3)
    log_func(msg+'\n'+tb_message)

def importOverride(name, glbls={}, lcls={}, fromlist=[], level=-1):
    """This is an override for __import__
        
    It first trys to import normally, but if it cannot it trys to 
    import files with .cc extensions, and if it does import a .cc file it 
    adds some magic to it.
    """
    module = None
    # First try the system __import__ first
    try:
        module = BUILTIN_IMPORT(name, glbls, lcls, fromlist, level)
        log.debug('Module %s loaded using builtin import' % name)
    except ImportError as error:
        # Next we will try to import them as a *.cc
        # First we need to determine if it exists
        # Check the folders in CC_PATH
        for path in CC_PATH:
            # If the path exists
            if os.path.exists(path):
                # And the path/<module name>.cc exists
                if os.path.exists(os.path.join(path, name+'.cc')):
                    # We will use the first one we find
                    # No the magic happens, we will first create a temp file
                    temp_file = tempfile.TemporaryFile()
                    # Now we add the 'magic' to the top of the temp file
                    temp_file.write(MAGIC)
                    # Now open the file being imported
                    module_file = open(os.path.join(path, name+'.cc'), 'r')
                    # Read the module contents into the temp file
                    temp_file.write(module_file.read())
                    module_file.close()
                    # Now rewind the temp file so it can be read from the beginning
                    temp_file.seek(0)
                    # Now import the module
                    try:
                        module = imp.load_module(name, temp_file, path, ('.cc', 'r', imp.PY_SOURCE))
                    except Exception as exception:
                        logError(sys.exc_info(), log.error, 'Error importing control code file %s.cc:' % name)
                    finally:
                        temp_file.close()
                    log.debug('Module %s loaded from %s using the special .cc import' % (name, path), MAGIC_LINE_NUMS)
        # If module is still None, we didn't find it and we should raise the original error
        if not module:
            raise error
    return module

def overrideImport():
    """Turns import overriding on"""
    # Replace __import__ with importOverride
    __builtins__["__import__"] = importOverride

def restoreImport():
    """Restores the default import mechanism"""
    # Restore __import__ with thre orignial import mechanism
    __builtins__["__import__"] = BUILTIN_IMPORT
