	
# This is a demonstration of out platform
# This method looks for objects
@service
def scanForObjects():
    from time import sleep
    triggerEvent('object found', 5, '50 Objects1')
    sleep(3)

@service
def scanForObjects2():
    from time import sleep
    triggerEvent('object found', 1, '50 Objects2')
    sleep(3)

# Called when the object found event is fired
def objectFound(data):
    log.info('Obstical Detected, Stopping... ' + str(data))

# This method gets called when the control code starts
def main():
    # Register callbacks to events
    #Stop the motors when an object is found
    register_callback('scanForObjects.object found', objectFound)
    register_callback('scanForObjects2.object found', objectFound)
    scanForObjects.start()
    scanForObjects2.start()
    # This method must be called to start handling events
    # It blocks until the control code exits
    handleEvents()
    