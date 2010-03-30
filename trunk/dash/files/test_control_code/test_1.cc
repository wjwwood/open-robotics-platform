from time import sleep

@service
def asdf():
    #triggerEvent('bob', 5, '50 Objects1')
    1/0
    log.info('hi')
    sleep(3)
    stop()
    log.info('You shouldn\'t see me')

def bob(msg):
    1/0
    log.info("You shouldn't see me!")

def main():
    asdf.start()
    registerCallback('asdf.bob', bob)
    handleEvents()