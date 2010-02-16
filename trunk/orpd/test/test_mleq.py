import unittest
import sys, os
sys.path.append(os.path.join('..', 'lib'))
from event_system import Event, MultiLevelEventQueue

class TestMultiLevelEventQueue(unittest.TestCase):
    def setUp(self):
        self.mleq = MultiLevelEventQueue()

    def test_init(self):
        mleq = MultiLevelEventQueue()
        tmp = { }
        for x in range(0, 10):
            tmp[x] = []
        self.assertEqual(mleq.evts, tmp)
    
    def test_addEvent(self):
        self.assertRaises(TypeError, self.mleq.addEvent, 'Yo')
        e = Event('lrf1', 'scanForObjects', 11, 'yo')
        self.assertRaises(TypeError, self.mleq.addEvent, 'Yo')
        e = Event('lrf1', 'scanForObjects', 1, 'yo')
        self.mleq.addEvent(e)
        a = self.mleq.retrieveEvent()
        self.assertEqual(e, a)
        
    def test_addFilter(self):
        e1 = Event('lrf1', 'scanForObjects', 1, 'yo')
        self.mleq.addEvent(e1)
        e2 = Event('lrf2', 'scanForObjects', 1, 'yo')
        self.mleq.addEvent(e2)
        self.mleq.filterEventType('lrf1')
        a = self.mleq.retrieveEvent()
        self.assertEqual(e2, a)
        self.mleq.unfilterEventType('lrf1')
        a = self.mleq.retrieveEvent()
        self.assertEqual(e1, a)
    
    def test_removeEventType(self):
        e1 = Event('lrf1', 'scanForObjects', 1, 'yo')
        self.mleq.addEvent(e1)
        e2 = Event('lrf2', 'scanForObjects', 1, 'yo')
        self.mleq.addEvent(e2)
        self.mleq.removeEventType('lrf1')
        a = self.mleq.retrieveEvent()
        self.assertEqual(e2, a)
        a = self.mleq.retrieveEvent()
        self.assertEqual(a, None)


if __name__ == '__main__':
    unittest.main()