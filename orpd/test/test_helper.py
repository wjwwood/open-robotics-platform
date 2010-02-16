"""
Runs all the tests
"""
import os
import sys
import unittest
import threading
import xmlrpclib as rpc

global proc, lock, pid
proc = None
lock = threading.Lock()
pid = None

def stopServer():
    """docstring for stopServer"""
    server = rpc.Server("http://localhost:7003")
    # Set a timeout
    from threading import Timer
    Timer(5, __kill).start()
    # Stop the server
    server.shutdown()
    # Wait for it to stop
    try:
        ret_code = proc.wait()
    except Exception:
        ret_code = proc.returncode
    return ret_code
    
def __kill():
    """Kills the server if it isn't dead yet"""
    ret_code = proc.poll()
    if ret_code == None:
        proc.kill()
    proc.wait()

def shutdown():
    """docstring for shutdown"""
    if proc is None or proc.poll():
        # The server isn't running
        return
    else:
        proc.kill()
        exit(0)

def echo():
    """docstring for echo"""
    import select
    while proc and not proc.poll():
        read, _, _ = select.select([proc.stdout],[],[],0.1)
        if read:
            print proc.stdout.readline(),

def startServerIfStopped():
    """Checks to see if the daemon has been started, if not it starts one"""
    global proc, lock, pid
    lock.acquire()
    if proc is None or proc.poll():
        # The server isn't running
        from subprocess import Popen, PIPE
        import time
        # Setup
        if os.getcwd()[-4:] == "test":
           os.chdir('../')
        if os.getcwd()[-3:] == "src" or os.getcwd()[-3:] == "orp":
           os.chdir('orpd/')
        # Start the Daemon
        proc = Popen("python orpd.py -w test/work_dirs/nominal/", shell=True, stdout=PIPE)
        time.sleep(0.5)
        if proc.poll():
           raise Exception("Robot Daemon never started.")
        server = rpc.Server("http://localhost:7003")
        # Wait for the server to be started
        while True:
            msg = proc.stdout.readline()
            if msg.strip() != '':
                print msg,
            if "Starting the server..." in msg:
                break;
        # Start the echo thread
        import thread
        pid = thread.start_new_thread(echo, ())
        lock.release()
        return proc, server
    else:
        lock.release()
        return proc, rpc.Server("http://localhost:7003")

if __name__ == '__main__':
    import test_general
    import test_logging
    import test_sandbox
    suites = []
    suites.append(unittest.TestLoader().loadTestsFromTestCase(
                    test_logging.ORPDLoggingTestCases))
    # suites.append(unittest.TestLoader().loadTestsFromTestCase(
    #                 test_sandbox.ORPDSandboxTestCases))
    suites.append(unittest.TestLoader().loadTestsFromTestCase(
                    test_general.ORPDGeneralTestCases))
    suite = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(suite)
    exit(0)
