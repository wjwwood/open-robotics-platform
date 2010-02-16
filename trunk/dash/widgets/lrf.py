"""
This is a widget for displaying Laser Range Finder data in the dashboard.
"""

if __name__ == '__main__':
    import sys
    sys.path.append('../')

import wx
import lib.elements as elements
import xmlrpclib
from threading import Lock

from numpy import arange, sin, pi
import numpy as np
import matplotlib
matplotlib.use('WX')
from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
import matplotlib.pyplot as plt

class LaserRangeFinderWidget(wx.Window):
    """Laser Range Finder Widget"""
    def __init__(self, parent, ID=-1, config=None):
        super(LaserRangeFinderWidget, self).__init__(parent, ID)
        self.parent = parent
        self.id = ID
        self.config = config
        
        # Create a connection to the Remote Server
        self.remote_server = xmlrpclib.Server('http://'+config+':7003/')
        
        # Create Panel
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('dark green')
        
        # Create the lrf display
        self.parent = parent
        self.lock = Lock()
        
        # Setup Matplotlib
        self.figure = plt.figure()
        self.axes = self.figure.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
        _theta = np.arange(-38.0, 232.3, 0.3515625)
        theta = []
        for i in _theta:
            if i < 0:
                i += 360
            theta.append(i)
        theta = [i*pi/180 for i in theta]
        radii = [1000 for x in range(0, 769)]
        
        self.line, = self.axes.plot(theta, radii)
        
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        # Create a button
        self.button = wx.Button(self, -1, 'Start Scanning...')
        self.button.Bind(wx.EVT_BUTTON, self.OnButton)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.button, 2, wx.CENTER | wx.BOTTOM)
        self.SetSizer(self.sizer)
        self.Fit()
        
        self.running = False
        
        self.period = 100
        TIMER_ID = 123456
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(self.period)
        wx.EVT_TIMER(self, TIMER_ID, self.refresh)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        wx.CallAfter(self.Layout)
        if __name__ != '__main__':
            wx.CallAfter(self.Hide)
        
    def refresh(self, event=None):
        """Refreshes the lrf data"""
        if not self.running:
            return
        # Set the data
        self.lock.acquire()
        radii = self.data = self.remote_server.lrf.scan()
        # Prepare the data
        i = 0
        for x in radii:
            if x > 1000:
                radii[i] = 20
            elif x < 20:
                radii[i] = 20
            i += 1
        # Update the graph
        self.line.set_ydata(radii)
        self.figure.canvas.draw_idle()
        self.lock.release()
        
    def OnClose(self, event=None):
        """docstring for OnClose"""
        self.timer.Stop()
        self.Destroy()
        
    def OnButton(self, event=None):
        """Called on the button press"""
        if self.running:
            # Stop
            self.running = False
            self.button.SetLabel('Start scanning...')
        else:
            self.running = True
            self.button.SetLabel('Stop scanning...')
    
def getWidget():
    """This is a manditory function that returns the widget to be created"""
    return LaserRangeFinderWidget
    
if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None, size=(640,540))
    frame.Show(True)
    LRF = LaserRangeFinderWidget(frame, config='localhost')
    app.MainLoop()