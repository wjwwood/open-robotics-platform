from time import sleep

def handleAngle(msg):
    log.info(str(msg).strip())

def handleAngleReached(msg):
    log.info("Angle Reached: %s" % msg.strip())
    stop()

@service
def timedStop():
    sleep(5)
    imu.pollToggle()
    registerCallback('imu.targetAngleReached', handleAngleReached)
    imu.turnToAngleDeferred(90)
    timedStop.stop()

def main():
    registerCallback('imu.angleReceived', handleAngle)
    imu.pollToggle()
    timedStop.start()
    handleEvents()