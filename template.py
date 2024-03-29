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
${TM_NEW_FILE_BASENAME}.py - <PURPOSE>

Created by ${TM_FULLNAME} on ${TM_DATE}.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

try: # try to catch any missing dependancies
# <PKG> for <PURPOSE>
    PKGNAME = '<EASY_INSTALL NAME>'
    import <LIBRARY NAME>

    del PKGNAME
except ImportError as PKG_ERROR: # We are missing something, let them know...
    sys.stderr.write(str(PKG_ERROR)+"\nYou might not have the "+PKGNAME+" \
module, try 'easy_install "+PKGNAME+"', else consult google.")

###  Class  ###


###  Functions  ###

def main():
	pass

###  IfMain  ###

if __name__ == '__main__':
	main()

