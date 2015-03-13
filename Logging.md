# Logging Documentation #

#This page documents the logs in ORP as well as sequences in which they occur.

This is important to document because the dashboard relies on the format of the messages to properly monitor the server.

## Format ##

Log consist of several elements:
  * Logger - This is the origin of the log message (ORPD, Sandbox, Control Code, HWM, etc...)
  * Log Level - This is the level of the log message (data, debug, info, warning, error, critical)
  * Log Message - This is the most important part to standardize and document (ex: `Server Ready`)


## ORP Server Logs ##

### Server Start-up ###
This section describes the Server starting for the first time and/or restarting

  1. **Logging**: This occurs when logging has started
    * ORPD
    * DEBUG
    * `Logger Started`
  1. **Working Directory**: Occurs when the working directory is set, which is after logging and configurations
    * ORPD
    * INFO
    * `Working Directory: <absolute working directory>`
  1. **Config File Does Not Exist**: Occurs conditionally if the given config file does not exist
    * ORPD
    * WARNING
    * `'<given config file name>' not present looking for orpd.cfg.default`
  1. **No Config files could be Found**: Occurs conditionally if the Server cannot find any config files
    * ORPD
    * CRITICAL
    * `No config files found, quitting...`
  1. **Work Directory Does Not Exist**: Occurs conditionally if the given work directory does not exist
    * ORPD
    * WARNING
    * `Work directory specified does not exist: <given work directory>`
  1. **Skipping Device**: Occurs conditionally if a device is disabled in the configuration files
    * ORPD
    * WARNING
    * `Device <device name> is disabled, skipping...`
  1. **Error Importing HWM**: Occurs conditionally if a HWM generates an Exception when being imported
    * ORPD
    * ERROR
    * `Error importing the module <name of the module>\n` and then followed with a Traceback
  1. **Device Class missing**: Occurs conditionally if a device class is not found in a HWM
    * ORPD
    * ERROR
    * `Could not find the Device Class for the <module name> Hardware Module so the device will be disabled, make sure the class name is spelled the same and that hyphens are replaced with underscores`
  1. **Exception In Device**: Occurs conditionally if an Exception occurs while constructing or calling init() on the device
    * ORPD
    * ERROR
    * `Exception in Device <module name>:\n` and then followed by a traceback
  1. **Missing Configuration**: Occurs conditionally a required configuration option is missing
    * ORPD
    * ERROR
    * `Manditory config '<missing config name>' not found for device '<module name>', the device will be disabled`
  1. **Server is Ready**: Occurs once all start functions have been completed
    * ORPD
    * INFO
    * `Server Ready`