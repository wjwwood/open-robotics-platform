"""
MDI AUI Parent Frame for the dashboard application, will contain the
rest of the windows for the dashboard.
"""
import wx.aui
import os.path

import lib.elements

from lib.builders.projectdrawer import ProjectDrawer
from lib.builders import console
from lib.builders import toolbar
from lib.builders import menu
import lib.log

class ParentFrame(wx.aui.AuiMDIParentFrame):
    """
    AUI Parent Frame
    """
    def __init__(self, ID=None, app_runner=None):
        # Give an id if it is not specified
        if not ID:
            ID = wx.NewId()
        self.id = ID
        self.app_runner = app_runner
        
        self.orp_data_buffer = None
        
        # File hashes
        self.files = self.buildListing()
        
        # Untitled Count
        self.count = 1
        
        # Create the window
        wx.aui.AuiMDIParentFrame.__init__(self, None, self.id,
                                          title="Dashboard",
                                          size=(1024,768),
                                          style=wx.DEFAULT_FRAME_STYLE)
        
        # Add Close Event
        wx.EVT_CLOSE(self, self.onClose)
        
        # Add hotkeys to window menu
        for item in self.GetWindowMenu().GetMenuItems():
            if item.Label == 'Previous':
                item.SetItemLabel(item.Label+'\tCtrl-{')
            if item.Label == 'Next':
                item.SetItemLabel(item.Label+'\tCtrl-}')
        
        # Store pointer in elements lib
        lib.elements.MAIN = self
        
        # Setup the logging System
        self.log = lib.log.start()
        
        # Configure and set the proj directory
        self.proj_dir = self.app_runner.project_dir
        # os.chdir(self.proj_dir)
        
        # Setup the aui manager
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        lib.elements.AUI_MANAGER = self._mgr
        
        # Setup Menus
        menu.Menus(self, self._mgr)
        
        # Construct and add the tool bar to the window
        toolbar.Toolbars(self, self._mgr)
        
        # Create the Project Drawer
        self.project_drawer = ProjectDrawer(self, self._mgr)
        
        # Create Log and Shell Consoles
        console.Consoles(self, self._mgr)
        
        # Status bar
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-2, -3])
        self.status_bar.SetStatusText("Ready", 0)
        self.status_bar.SetStatusText("ORPD", 1)
        lib.elements.STATUS_BAR = self.status_bar
        
        # Load saved Perspective and window size if there is one
        try:
            perspective_save = open(os.path.join(self.app_runner.usr_home, 'dashboard.Perspective'), 'r')
            perspective = perspective_save.read().strip()
            self._mgr.LoadPerspective(perspective)
        except: pass
        
        try:
            window_size_save = open(os.path.join(self.app_runner.usr_home, 'dashboard.window_size'), 'r')
            window_size = window_size_save.read().strip().split(" ")
            window_size[0] = int(window_size[0])
            window_size[1] = int(window_size[1])
            window_size[2] = int(window_size[2])
            window_size[3] = int(window_size[3])
            self.SetSize(wx.Size(window_size[0], window_size[1]))
            self.Move(wx.Point(window_size[2], window_size[3]))
        except: pass
        
        self._mgr.Update()
        
    def onClose(self, event):
        """Called on close"""
        # Save the Perspective
        perspective = self._mgr.SavePerspective()
        perspective_save = open(os.path.join(self.app_runner.usr_home, 'dashboard.Perspective'), 'w+')
        perspective_save.write(perspective)
        perspective_save.close()
        
        # Save window size
        window_size = ""
        size = self.GetSize()
        x,y = size.x, size.y
        window_size += str(x)+" "
        window_size += str(y)+" "
        pos = self.GetPosition()
        x,y = pos.x, pos.y
        window_size += str(x)+" "
        window_size += str(y)+" "
        window_size_save = open(os.path.join(self.app_runner.usr_home, 'dashboard.window_size'), 'w+')
        window_size_save.write(window_size)
        window_size_save.close()

    def buildListing(self):
        """Build a listing of the files in files and modules for connection"""
        cc_list = self.walkDirectory(os.path.join(os.getcwd(), 'files'))
        module_list = self.walkDirectory(os.path.join(os.getcwd(), 'modules'))
        return (cc_list, module_list)

    def walkDirectory(self, root_path):
        """A helperfunction that walks directories"""
        listing = {}
        for root, dirs, files in os.walk(root_path):
            abs_path = root.replace(root_path, '')[1:]
            paths = abs_path.split(os.sep)
            base_listing = listing
            for path in paths:
                if len(path):
                    if path in base_listing:
                        base_listing = base_listing[path]
            for d in dirs:
                if d[0] == '.':
                    continue
                # if d in base_listing:
                base_listing[d] = {}
            for f in files:
                if f[0] != '.' and not f.endswith(('.hwmo', '.hwmc', \
                                                   '.pyo', '.pyc', \
                                                   '.cco', '.ccc')):
                    full_path = os.path.join(root_path, abs_path, f)
                    base_listing[f] = (full_path, os.stat(full_path)[8])
        return listing