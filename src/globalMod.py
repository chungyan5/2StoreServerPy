'''
Filename: globals.py
Description: keep global variabls  
@author: yan, chungyan5@gmail.com, 2Store
'''

## import other libraries
##################################################

### configuration file parser library 
import ConfigParser

## list the global variables, all Parameters listed here for this application      
##################################################

### path sync devices under owncloud user folder 
SYNC_PATH = "/files/Sync_Devices/"

### .para location    
paraFile = ".para"                  # fixed at current folder

### .logfile configuration file location    
logFile = ".logging"

## init. the global variables, this function is called by main()      
##################################################
def init():
    
## Configuration file for different parameters
    global configFile
    configFile = ConfigParser.ConfigParser() 
    configFile.read(paraFile)
    
## Base Path for the owncloud folder 
    global basePath 
    basePath = configFile.get("default", "BASE_PATH")
    
## fixed regular interval to operation, in second unit 
    global reg_period
    reg_period = float(configFile.get("default", "REG_PERIOD"))

def getBasePath():
    global basePath
    return basePath
    
def getConfigFile():
    global configFile
    return configFile

def getRegPeriod():
    global reg_period 
    return reg_period
