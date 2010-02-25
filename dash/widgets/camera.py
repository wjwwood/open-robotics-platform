import wx
# import lib.elements as elements
import xmlrpclib
import Image
import base64
from threading import Lock

class CameraWidget(wx.Window):
    """Laser Range Finder Widget"""
    def __init__(self, parent, ID=-1, config='localhost'):
        wx.Window.__init__(self, parent, ID)
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

        self.button = wx.Button(self, -1, 'Get Pictures', pos=(10, 5))
        self.button.Bind(wx.EVT_BUTTON, self.onButton)
        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        # self.sizer.Add(self.button, 1, wx.CENTER | wx.BOTTOM)
        
        try:
            jpg = wx.EmptyImage(200, 200).ConvertToBitmap()
            # bitmap upper left corner is in the position tuple (x, y) = (5, 5)
            self.bitmap = wx.StaticBitmap(self, bitmap=jpg, pos=(20, 30), size=(200,300))
            # self.sizer.Add(self.bitmap, 1, wx.CENTER | wx.GROW | wx.TOP)
        except IOError:
            print "Image file %s not found" % imageFile
            raise SystemExit

        # self.SetSizer(self.sizer)
        self.Fit()

        self.running = False
        
        self.period = 1000
        TIMER_ID = wx.NewId()
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(self.period)
        wx.EVT_TIMER(self, TIMER_ID, self.refresh)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        wx.CallAfter(self.Layout)
        if __name__ != '__main__':
            wx.CallAfter(self.Hide)
        
    def refresh(self, event=None):
        """Refreshes the lrf data"""
        if not self.running:
            return
        # Set the data
        with self.lock:
            import time
            a = time.time()
            self.data = self.remote_server.cam1.getImage()
            b = time.time()
            print b - a 
        if self.data:
            pi = Image.fromstring("RGB", (self.data[0], self.data[1]),  base64.b64decode(self.data[4]))
            wximg = wx.EmptyImage(self.data[0], self.data[1])
            wximg.SetData(pi.convert("RGB").tostring())
            wximg.SetAlphaData(pi.convert("RGBA").tostring()[3::4])
            self.bitmap.SetBitmap(wx.BitmapFromImage(wximg))
        
    def onClose(self, event=None):
        """docstring for OnClose"""
        self.timer.Stop()
        self.Destroy()
        
    def onButton(self, event=None):
        """Called on the button press"""
        if self.running:
            # Stop
            self.running = False
            self.button.SetLabel('Stop')
        else:
            self.running = True
            self.button.SetLabel('Get Pictures')
    
def getWidget():
    """This is a manditory function that returns the widget to be created"""
    return CameraWidget
    
if __name__ == '__main__':
    app = wx.App(0)
    frame = wx.Frame(None, size=(670,540))
    camera = CameraWidget(frame, config='192.168.2.2')
    frame.Show(True)
    app.MainLoop()