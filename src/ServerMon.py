#!/usr/bin/python
# Filename: ServerMon.py
# Description: Server Monitoring tasks
#                1) auto. Change from offline to online mode after meet a 90% full 
# Attention for running this script: must be run in superuser or www-data user daemon 
# Author: yan, chungyan5@gmail.com, 2Store   
##################################################

## import other libraries
##################################################

### daemon library 
from daemon import runner

### configuration file parser library 
import ConfigParser

### logging library 
import logging.config

### daemon time and datetime 
import time
import datetime

### Offline and Online Mode 
from OffOnlineMode import OffOnlineMode

## This Application Class     
##################################################

class DaemonApp():
    
    def __init__(self, reg_period):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path =  '/tmp/serverMod.pid'
        self.pidfile_timeout = 5
        
        self.reg_period = reg_period        # fixed regular interval to operation, in second unit
        self.offOnlineMode = OffOnlineMode(basePath, syncPath)
        
    def run(self):
        
## init. Before looping    
##################################################

### clear end time, start time 
        startTime = datetime.datetime.now()
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=self.reg_period+1)  # let it to be > reg_period, so start to operate immediately  
    
### read in parameter of between jobs interval time (in second unit)
         
## looping     
##################################################
        while True: 

### verify the interval time     
##################################################

####     operation time = end time - start time, in second unit  
            #operationTime = endTime - startTime
            #operationTimeSec = operationTime.total_seconds()
            operationTimeSec = (endTime - startTime).total_seconds()

####     if NOT operation time > between jobs interval time
####        waiting time = between jobs interval time - operation time 
####        sleeping for waiting time period
            if operationTimeSec < self.reg_period:
                # waiting time in second unit 
                waitTime = self.reg_period - operationTimeSec
                #waitTime = self.reg_period
                serverModLogger.debug('wait time (in Second) %s', waitTime)
                time.sleep(float(waitTime))
                
### keep the start time     
##################################################
            startTime = datetime.datetime.now()

### Offline and Online Mode 
##################################################
            self.offOnlineMode.execution()

### keep the end time and loop back
##################################################
            endTime = datetime.datetime.now()

## get optional arguments   
#################################
paraFile = ".para"                  # fixed at current folder
logFile = ".logging"

## setup Configuration file for different parameters  
#################################

## prepare Configuration file
config = ConfigParser.ConfigParser() 
config.read(paraFile) 
basePath = config.get("default", "BASE_PATH")

## logging setting 
##################################################
logging.config.fileConfig(logFile)
serverModLogger = logging.getLogger('ServerMon')
serverModLogger.info('===========================================')
serverModLogger.info('Start info message from Main Server Monitor')

## all Parameters listed here for this module 
##################################################
syncPath = "/files/Sync_Devices/"

## call daemon library
##################################################
## This Class Server Monitor Daemon Content    
##################################################
app = DaemonApp(float(config.get("default", "REG_PERIOD")))
daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[serverModLogger.handlers[0].stream]    # This ensures that the logger file handle does not get closed during daemonization
                                                                                    #    reference: http://stackoverflow.com/questions/4375669/logging-in-python-with-config-file-using-handlers-defined-in-file-through-code
daemon_runner.do_action()
