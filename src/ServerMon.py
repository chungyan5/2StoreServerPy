#!/usr/bin/python
# Filename: ServerMon.py
# Description: Server Monitoring tasks
#                1) auto. Change from offline to online mode after meet a 90% full 
# Attention for running this script: must be run in superuser or www-data user by Cron regularly 
# Author: yan, chungyan5@gmail.com, 2Store   
##################################################

## import other libraries
import argparse  
import ConfigParser
import logging.config
from AutoOff2Online import AutoOff2Online

## get optional arguments   
#################################
parser = argparse.ArgumentParser(description='2store Server Monitoring')
parser.add_argument('-p', type=str, 
                   help='the config files path (.para and .logging)')
args = parser.parse_args()
if args.p == None:
    paraFile = ".para"                  # at current folder
    logFile = ".logging"
else:
    paraFile = args.p + ".para"
    logFile = args.p + ".logging"

## setup Configuration file for different parameters  
#################################

## prepare Configuration file
config = ConfigParser.ConfigParser() 
config.read(paraFile) 
basePath = config.get("default", "BASE_PATH")
 
## all Parameters for this module 
##################################################
syncPath = "/files/Sync_Devices/"

## logging setting 
##################################################
logging.config.fileConfig(logFile)
serverModLogger = logging.getLogger('ServerMon')
serverModLogger.info('===========================================')
serverModLogger.info('Start info message from Main Server Monitor')

## auto. Change from offline to online mode after meet a 90% full 
##################################################
autoOff2Online = AutoOff2Online(basePath, syncPath, serverModLogger)
autoOff2Online.off2Online()
# os.system("/bin/date >> /tmp/2.txt")

