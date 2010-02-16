"""
Paster commands for an easy way of starting the system.

Two main commands, one starts the dashboard, the other will open a
remote shell to the robot through python.
"""

import sys, os
import wx
from optparse import OptionParser
import lib.elements

def main():
    """
    Main Command function to run the args.
    """
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-l", "--log_level", dest="log_level",
                      help="set the log level")
                      
    parser.add_option("-d", "--dir", dest="dir",
                    help="set the working directory")
                    
    (options, args) = parser.parse_args()
    if options.log_level:
        print "reading %s..." % options.log_level
        
    if options.dir:
        work_dir = options.dir
    else:
        work_dir = os.getcwd()
    
    if (len(args) and args[0] == 'start') or not args:
        sys.path.append(sys.path[0])
        from lib.app_runner import AppRunner
        AppRunner(os.path.join(work_dir, 'config')).start()

if __name__ == "__main__":
    main()
