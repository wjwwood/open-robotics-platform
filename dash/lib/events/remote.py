"""
Remote event call object, for when the dashboard sends a message to 
the GUI components.
"""
import wx

WXCONSOLE = wx.NewEventType()
# bind to serial data receive events
EVT_WXCONSOLE = wx.PyEventBinder(WXCONSOLE, 0)

class RemoteCallEvent(wx.PyCommandEvent):
    """
    RemoteCallEvent object to store remote calls from the robot to
    the GUI.
    """

    eventType = WXCONSOLE
    def __init__(self, window_id, data):
        wx.PyCommandEvent.__init__(self, self.eventType, window_id)
        self.data = data

