# Open Robotics Platform #

---

The Open Robotics Platform(ORP) is an open source, easy to use rapid robot development platform.  It is is written in pure Python and consists of two main components.  First, there is the Server or Daemon which is the process that runs on your robot platform and handles hardware interfacing and control code execution.  Secondly, there is the Dashboard which is a GUI written in wxpython that provides a nice, integrated front end to the Server.  The Dashboard has an editor for authoring Hardware Modules (like drivers for ORP) and control code.  It provides controls for manipulating the Server so you don't spend all your time in an SSH terminal.  It also provides a method for using 'Widgets' to visualize sensor and device data from your robot platform.