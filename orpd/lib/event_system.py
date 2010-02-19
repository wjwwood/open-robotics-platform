import threading

class Event(object):
    "Event Container"
    def __init__(self, name, data, object, callbacks, log):
        """  
        Initialize the object variables
        
        Potential ways of calling this:
          Event("name", data)
          Event("name", data, "object")
          Event("object.name", data)
        """
        self.obj = obj
        self.name = name
        self.data = data
        self.log = log
        self.callbacks = callbacks

    def __call__(self):
        import sys
        ref = self.obj+'.'+self.name
        if self.callbacks.has_key(ref):
            self.callbacks[ref](self.data)
        else:
            self.log.warning("No registered callback for %s" % ref)
    
class MultiLevelEventQueue(object):
    "Multi-Level Event Queue"
    def __init__(self):
        "Setup the Multi-Level Event Queue"
        self.evts = {}
        self.filter = []
        self.priority_map = {}
        for x in range(0, 10):
            self.evts[x] = []

    def registerCallback(self, ref_name, func, priority = 5):
        "Register Callbacks with the event systems"
        pass

    def setPriority(self, ref_name, priority = 5):
        ""
        pass

    def triggerEvent(self, name, data, obj_name=None):
        """Allows Control Code to trigger events"""
        split_name = name.split('.')
        if len(split_name) == 2:
            obj_name = split_name[0]
            name = split_name[1]
        else:
            if not obj_name:
                obj_name = traceback.extract_stack()[-2][2]

        event = [obj_name, name, data]
        self.queue.put(event)

    def addEvent(self, evt):
        "Adds an event to the queue"
        if not isinstance(evt, Event) or (evt.priority < 0 or evt.priority > 10):
            raise TypeError('Event object passed is not of the correct type')
        # inserts it into the front of the List
        self.evts[evt.priority].insert(0, evt) 
        
    def removeEventType(self, type):
        "Remove a filter to the retrievable events."
        for x in range(0, 10):
            if len(self.evts[x]):
                for y in self.evts[x]:
                    if y.obj == type:
                        self.evts[x].remove(y)

    def filterEventType(self, type):
        "Add a filter to the retrievable events."
        self.filter.append(type)
    
    def unfilterEventType(self, type):
        "Remove a filter to the retrievable events."
        self.filter.remove(type)

    def retrieveEvent(self):
        "Get the next event"
        for x in range(0, 10):
            if len(self.evts[x]):
                for y in self.evts[x]: 
                    if y.obj not in self.filter:
                        # remove the 0 index item
                        return self.evts[x].pop(0)
