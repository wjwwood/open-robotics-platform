import threading

class Event(object):
    "Event Container"
    def __init__(self, obj, name, priority, data, callbacks, log):
        "Initialize the object variables"
        self.obj = obj
        self.name = name
        self.priority = priority
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
        for x in range(0, 10):
            self.evts[x] = []

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
