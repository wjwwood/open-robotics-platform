import logging
from lib.events.log import LogRxEvent

class NetworkEventHandler(logging.Handler):
    """
    Handles network events, for the remote logging system.
    """
    win_id = None
    handler = None
    def __init__(self, strm=None):
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            msg = self.format(record)
            event = LogRxEvent(self.win_id, msg)
            self.handler.AddPendingEvent(event)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

