import wx
import lib.elements

ID_NEW_FILE  = wx.NewId()
ID_NEW_PROJECT = wx.NewId()
ID_OPEN_FILE = wx.NewId()
ID_OPEN_PROJECT = wx.NewId()
ID_SAVE = wx.NewId()
ID_CLOSE_WINDOW = wx.NewId()
ID_CONSOLE = wx.NewId()
ID_SAVE = wx.NewId()
ID_SAVE_LOGS = wx.NewId()
ID_EXIT = wx.NewId()

ID_PROJECT_DRAWER = wx.NewId()
ID_LRF_DEMO = wx.NewId()

class Menus(object):
    def __init__(self, parent, mgr):
        self.parent = parent
        self.mgr = mgr
        
        lib.elements.MENUS = self
        
        # Create the Menubar
        self.menubar = wx.MenuBar()
        
        # Create the menus
        self.createFileMenu()
        self.createViewMenu()
        
        # Set the menubar
        parent.SetMenuBar(self.menubar)
        
    def createFileMenu(self):
        """Creates, Adds items to, and binds events to the File Menu"""
        # Create the File Menu
        file_menu = self.file_menu = wx.Menu()
        lib.elements.FILE_MENU = file_menu
        
        # Add the items to the menu
        file_menu.Append(ID_NEW_FILE, "&New File\tCtrl-N")
        # file_menu.Append(ID_NEW_PROJECT, "New Project")
        file_menu.AppendSeparator()
        file_menu.Append(ID_OPEN_FILE, "Open File\tCtrl-O")
        # file_menu.Append(ID_OPEN_PROJECT, "Open Project")
        file_menu.Append(ID_SAVE, "Save\tCtrl-S")
        file_menu.AppendSeparator()
        file_menu.Append(ID_SAVE_LOGS, "Save Logs as...\tCtrl-L")
        file_menu.AppendSeparator()
        file_menu.Append(ID_CLOSE_WINDOW, "Close Window\tCtrl-W")
        file_menu.AppendSeparator()
        file_menu.Append(ID_EXIT, "E&xit")
        
        # Bind Events to the Menu Items
        from lib.events import editor
        self.parent.Bind(wx.EVT_MENU, editor.newFile, id=ID_NEW_FILE)
        self.parent.Bind(wx.EVT_MENU, editor.openFile, id=ID_OPEN_FILE)
        from lib.events.localfiles import saveFile
        self.parent.Bind(wx.EVT_MENU, saveFile, id=ID_SAVE)
        from lib.events.log import saveLogs
        self.parent.Bind(wx.EVT_MENU, saveLogs, id=ID_SAVE_LOGS)
        self.parent.Bind(wx.EVT_MENU, editor.close, id=ID_CLOSE_WINDOW)
        from lib.events import menu
        self.parent.Bind(wx.EVT_MENU, menu.quit, id=ID_EXIT)
        
        # Add the File Menu to the Menubar
        self.menubar.Append(file_menu, "&File")
        
    def createViewMenu(self):
        """Creates, Adds items to, and binds events to the View Menu"""
        # Create the View Menu
        view_menu = self.view_menu = wx.Menu()
        lib.elements.VIEW_MENU = view_menu
        
        # Add the items to the menu
        view_menu.AppendCheckItem(ID_PROJECT_DRAWER, "Project Drawer")
        view_menu.AppendCheckItem(ID_LRF_DEMO, "View LRF Data")
        
        # Bind Events to the Menu Items
        from lib.events import menu
        self.parent.Bind(wx.EVT_MENU, menu.toggleProjectDrawer, id=ID_PROJECT_DRAWER)
        self.parent.Bind(wx.EVT_MENU, menu.openLRFData, id=ID_LRF_DEMO)
        
        # Add the View Menu to the Menubar
        self.menubar.Append(view_menu, "&View")