"""
An application management class to simplify controling the overall process.
"""
import wx
import logging
import logging.config
import os
import ConfigParser
from lib.log.network import NetworkEventHandler
import lib.frames.main

class Config(object):
    """
    Configuration management class
    """
    configure = {}
    
    @classmethod
    def setup_env(cls, config_path):
        """
        Loads Config and runs some enviorment setup functions
        """
        if os.path.isfile(os.path.join(config_path, 'log.cfg')):
            cls.configure['log'] = logging.config.fileConfig(os.path.join(config_path, 'log.cfg'))
        else:
            cls.configure['log'] = logging.config.fileConfig(os.path.join(config_path, 'log.cfg.default'))
            
        if os.path.isfile(os.path.join(config_path, 'dash.cfg')):
            cls.configure['cfg'] = True
        else:
            cls.configure['cfg'] = False

class AppRunner(object):
    """
    Process management class, controls configs, and the wx processes
    """
    def __init__(self, config_path, *args, **kwargs):
        """
        Initialize any applicaiton settings in this function.
        """
        self.app = wx.App(0)
        self.dash_config_path = config_path
        self.dash_config = Config.setup_env(config_path)
        
        self.usr_home = os.getenv('USERPROFILE') or os.getenv('HOME')
        self.usr_home = os.path.join(self.usr_home, '.orp')
        try:
            os.mkdir(self.usr_home)
        except OSError:
            pass
        self.config = ConfigParser.ConfigParser()
        self.config.read([os.path.join(config_path, 'defaults.cfg'), os.path.join(self.usr_home, '.orpd.cfg')])
        
        self.project = self.config.get('Projects', 'current')
        self.project_dir = self.config.get(self.project, 'working_dir')
        self.usr_cfg_file = os.path.join(self.usr_home, '.orpd.cfg')
        
        with open(self.usr_cfg_file, 'w+') as configfile:
            self.config.write(configfile)
            
    def start(self):
        """
        Start the main app process
        """ 
        window_id = wx.NewId()
        parent_frame = lib.frames.main.ParentFrame(window_id, self)
        
        parent_frame.Show(True)
        self.app.SetTopWindow(parent_frame)
        self.app.MainLoop()
        
