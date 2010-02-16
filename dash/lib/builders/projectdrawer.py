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
projectdrawer.py - Contains/Builds the project drawer

Created by William Woodall on 2009-11-08.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other Libraries
import lib.elements
from lib.events import projectdrawer

try: # try to catch any missing dependancies
# wx for window elements
    PKGNAME = 'wxpython'
    import wx
    import wx.aui as aui
    from wx.lib.mixins.treemixin import ExpansionState

    del PKGNAME
except ImportError as PKG_ERROR: # We are missing something, let them know...
    sys.stderr.write(str(PKG_ERROR)+"\nYou might not have the "+PKGNAME+" \
            module, try 'easy_install "+PKGNAME+"', else consult google.")

###  Class  ###

class MyTreeCtrl(ExpansionState, wx.TreeCtrl):
    """Tree with ExpansionState Mixin"""
    def __init__(self, *args, **kwargs):
        wx.TreeCtrl.__init__(self, *args, **kwargs)
        
    def GetItemIdentity(self, item):
        """Overrides the default function to return the label rather than the index"""
        return self.GetItemText(item)
        

class ProjectDrawer(object):
    """Project Drawer"""
    def __init__(self, parent, mgr):
        self.parent = parent
        self.mgr = mgr
        
        # Create the AUI Notebook
        self.drawer = wx.aui.AuiNotebook(parent, -1, wx.DefaultPosition, wx.Size(180, 250), 
                            wx.aui.AUI_NB_DEFAULT_STYLE | wx.aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER)
        
        # Create the CC tree
        cc_tree = MyTreeCtrl(parent, -1, wx.DefaultPosition, wx.Size(180, 250),
                           wx.TR_HIDE_ROOT | wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        self.cc_tree = cc_tree
        
        # Create the Module tree
        hwm_tree = MyTreeCtrl(parent, -1, wx.DefaultPosition, wx.Size(180, 250),
                           wx.TR_HIDE_ROOT | wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        
        self.hwm_tree = hwm_tree
        
        # Setup the images for the folders
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, 
            wx.ART_OTHER, wx.Size(16, 16)))
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, 
            wx.ART_OTHER, wx.Size(16, 16)))
        cc_tree.AssignImageList(imglist)
        hwm_tree.AssignImageList(imglist)
        
        # Flesh out the tree using the current working directory
        self.buildTree(self.cc_tree, lib.elements.MAIN.files[0])
        self.buildTree(self.hwm_tree, lib.elements.MAIN.files[1])
        
        # Bind events
        parent.Bind(wx.EVT_TREE_SEL_CHANGED, projectdrawer.selected, cc_tree)
        parent.Bind(wx.EVT_TREE_ITEM_COLLAPSED, projectdrawer.expansionStateChanged, cc_tree)
        parent.Bind(wx.EVT_TREE_ITEM_EXPANDED, projectdrawer.expansionStateChanged, cc_tree)
        parent.Bind(wx.EVT_TREE_ITEM_ACTIVATED, projectdrawer.activated, cc_tree)
        parent.Bind(wx.EVT_TREE_SEL_CHANGED, projectdrawer.selected, hwm_tree)
        parent.Bind(wx.EVT_TREE_ITEM_COLLAPSED, projectdrawer.expansionStateChanged, hwm_tree)
        parent.Bind(wx.EVT_TREE_ITEM_EXPANDED, projectdrawer.expansionStateChanged, hwm_tree)
        parent.Bind(wx.EVT_TREE_ITEM_ACTIVATED, projectdrawer.activated, hwm_tree)

        
        self.drawer.AddPage(self.cc_tree, "CC")
        self.drawer.AddPage(self.hwm_tree, "HWM")
        
        # Add to the AUI Manager
        mgr.AddPane(self.drawer, wx.aui.AuiPaneInfo().
                Name("Project Drawer").Left().Layer(1).Position(1).
                CloseButton(True).MaximizeButton(True))
        lib.elements.PROJECT_DRAWER = self
        
        # Restore the state iff there is one
        try:
            import pickle
            state_file = open(os.path.join(lib.elements.MAIN.app_runner.usr_home, 'expansion.state'), 'r')
            self.cc_tree.SetExpansionState(pickle.load(state_file))
        except IOError:
            pass
        
    def updateList(self):
        """Updates the tree"""
        # Try and preserve the state
        # TODO: this method of preserving state can be problemmtic with certain folder trees
        self.expansion_states = []
        self.expansion_states.append(self.cc_tree.GetExpansionState())
        self.expansion_states.append(self.hwm_tree.GetExpansionState())
        self.cc_tree.DeleteAllItems()
        self.hwm_tree.DeleteAllItems()
        lib.elements.MAIN.files = lib.elements.MAIN.buildListing()
        self.buildTree(self.cc_tree, lib.elements.MAIN.files[0])
        self.buildTree(self.hwm_tree, lib.elements.MAIN.files[1])
        self.cc_tree.SetExpansionState(self.expansion_states[0])
        self.hwm_tree.SetExpansionState(self.expansion_states[1])
        
    def traverse(self, parent=None):
        """Traverses the tree"""
        if parent is None:
            parent = self.tree.GetRootItem()
            nc = self.tree.GetChildrenCount(parent, False)

        def GetFirstChild(parent, cookie):
            return self.tree.GetFirstChild(parent)

        GetChild = GetFirstChild
        cookie = 1
        for i in range(nc):
            child, cookie = GetChild(parent, cookie)
            GetChild = self.tree.GetNextChild
            yield child
            
    def __buildTreeHelper(self, tree, ids, parent, path):
        # for filename, date in path.iteritems():
        for x in path:
            if isinstance(path[x], dict):
                if parent == None:
                    ids[x] = tree.AddRoot(x)
                else:
                    ids[x] = tree.AppendItem(ids[parent], x)
                self.__buildTreeHelper(tree, ids, x, path[x])
            else:
                item_data = wx.TreeItemData(path[x])
                tree.AppendItem(ids[parent], x, data=item_data)
        
    def buildTree(self, tree, file_listing):
        """Builds the tree from the cwd"""
        root = 'You shouldnt see me!'
        ids = {root : tree.AddRoot(os.path.basename(root))}
        self.__buildTreeHelper(tree, ids, root, file_listing)

