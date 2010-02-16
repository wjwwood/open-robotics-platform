import wx
import os

import lib.elements as elements

LOGRX = wx.NewEventType()
EVT_LOGRX = wx.PyEventBinder(LOGRX, 0)

class LogRxEvent(wx.PyCommandEvent):
    """
    Remote Log Event handler, for displaying logs in the daskboard console
    """
    eventType = LOGRX
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)


def logReceived(event):
    """This function is called when a log has been received and needs
    to be posted to the log console"""
    msg = event.data
    elements.LOG_CONSOLE.AppendText(msg)
    
def saveLogs(event=None):
    """Saves the logs in the log console to a file"""
    # Ask for the File path
    dlg = wx.FileDialog(elements.MAIN, "Save your log file to...", os.getcwd(), "", "*.*", \
                        wx.SAVE | wx.OVERWRITE_PROMPT)
    if dlg.ShowModal() != wx.ID_OK:
        return
    filename = dlg.GetFilename()
    dirname = dlg.GetDirectory()
    path = os.path.join(dirname, filename)
    # Get the contents of the log console
    contents = elements.LOG_CONSOLE.GetValue()
    # Save the contents to the file
    file_obj = open(path, 'w+')
    file_obj.write(contents)
    file_obj.close()