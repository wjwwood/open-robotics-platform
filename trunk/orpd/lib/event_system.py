"""
event_system.py - Event handling services for the daemon.

The MultiLevelEventQueue is where all the event handling happens. 
The Event object is simply a container object for events.
"""
__author__ = "John Harrison"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

import traceback
import logging
callbacks = {}
log = logging.getLogger("ControlCode")

class Event(object):
    "Event Container Object."
    def __init__(self, name, data, object):
        """ 
        Initialize the object variables
        """
        self.obj = object
        self.name = name
        self.data = data

    def nameRef(self):
        """
        A name reference for the Event, its used within the queue to find
        which event masks apply for this event. Lowest priority is *.*
        """
        return [
                self.obj + '.' + self.name, 
                self.obj + '.*', 
                '*.' + self.name,
                "*.*"
            ]

    def __call__(self):
        ref = self.obj+'.'+self.name
        if callbacks.has_key(ref):
            callbacks[ref](self.data)
        else:
            log.warning("No registered callback for %s" % ref)

# TODO: This doesn't check if the objects are valid objects
class MultiLevelEventQueue(object):
    "Multi-Level Event Queue"
    def __init__(self, queue, lock):
        "Setup the Multi-Level Event Queue"
        self.evts = {}
        self.filter = []
        self.priority_map = { '*' : { '*' : 5 }}
        self.queue = queue
        self.lock = lock
        for x in range(0, 10):
            self.evts[x] = []

    def registerCallback(self, ref_name, func, priority = None):
        "Register Callbacks with the event systems"
        self.__isValid(ref_name)
        callbacks[ref_name] = func
        if priority:
            self.setPriority(ref_name, priority) 

    def setPriority(self, ref_name, priority = 5):
        "Publicly accessable setPriority"
        if priority > 0 and priority <= 10:
            self._setPriority(ref_name, priority)
        else:
            raise TypeError('priority value is invalid')

    def _setPriority(self, ref_name, priority):
        """
        Sets the priority in our priority map, then removes any applicable 
        events from the queue and re-adds them. 
        
        This means if you change the priority of an event type while an 
        event of that type is already in the queue, it gets moved to the
        new level and gets pushed back to the end of that level of the queue.
        """
        ref_name = self.__isValid(ref_name)
        if ref_name[0] == '*':
            self.priority_map[ref_name[0]][ref_name[1]] = priority
        else:
            if ref_name[0] not in self.priority_map:
                self.priority_map[ref_name[0]] = {}
            self.priority_map[ref_name[0]][ref_name[1]] = priority
        events = []
        for level in range(0, 10):
            if len(self.evts[level]):
                for evt in self.evts[level]:
                    if (evt.obj == type[0] or evt.obj == '*') \
                            and (evt.name == type[1] or evt.name == '*'):
                        events.append(evt)
                        self.evts[level].remove(evt)
        for evt in events:
            self.addEvent(evt)

    def triggerEvent(self, name, data, obj_name=None):
        """Allows Control Code to trigger events"""
        split_name = name.split('.')
        if len(split_name) == 2:
            obj_name = split_name[0]
            name = split_name[1]
        else:
            if not obj_name:
                # TODO check this value
                obj_name = traceback.extract_stack()[-2][2] 
        self.addEvent(Event(name, data, obj_name))

    def __filter(self, x):
        "Event filter function"
        return x in self.filter

    def addEvent(self, evt):
        "Adds an event to the queue"
        if not isinstance(evt, Event):
            raise TypeError('Event object passed is not of the correct type')
        # inserts it into the front of the List
        if not filter(self.__filter, evt.nameRef()):
            try:
                self.evts[self.priority_map[evt.obj][evt.name]].append(evt)
            except KeyError:
                try:
                    self.evts[self.priority_map[evt.obj]['*']].append(evt)
                except KeyError:
                    try:
                        self.evts[self.priority_map['*'][evt.name]].append(evt)
                    except KeyError:
                        self.evts[self.priority_map['*']['*']].append(evt)
        else: 
            log.debug("Event is being filtered.")
    
    def __isValid(self, type):
        if not isinstance(type, (str, unicode)):
            # TODO: type = str(type) possible?
            raise TypeError('Event Identifier needs to be a string')
        if len(type.split('.')) != 2:
            raise TypeError('Event Identifier is malformed.')
        return type.split('.')
        
    def removeEventType(self, type):
        """
        Remove a filter to the retrievable events.
        type format:
            object.name
            object.*
            *.name
        """
        type = self.__isValid(type)
        for level in range(0, 10):
            if len(self.evts[level]):
                for evt in self.evts[level]:
                    if (evt.obj == type[0] or evt.obj == '*') \
                            and (evt.name == type[1] or evt.name == '*'):
                        self.evts[level].remove(evt)

    def filterEventType(self, type):
        "Add a filter to the retrievable events. "
        self.__isValid(type)
        self.filter.append(type)
    
    def unfilterEventType(self, type):
        "Remove a filter to the retrievable events."
        self.__isValid(type)
        self.filter.remove(type)

    def retrieveEvent(self):
        "Get the next event"
        for level in range(0, 10):
            if len(self.evts[level]):    
                # remove the 0 index item, since the queue is FIFO
                log.debug("Event triggered at priority %s" % level)
                return self.evts[level].pop(0)
