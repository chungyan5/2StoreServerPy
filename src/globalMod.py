'''
Filename: globals.py
Description: keep global variabls  
@author: yan, chungyan5@gmail.com, 2Store
'''

## import other libraries
##################################################

### configuration file parser library 
import ConfigParser

### file names matching library and file system searching 
import fnmatch
import os.path

## list the global variables, all Parameters listed here for this application      
##################################################

### path sync devices under owncloud user folder
SYNC_DEVICES = "Sync_Devices"
SYNC_PATH = "/files/" + SYNC_DEVICES + "/"

### .para location    
paraFile = ".para"                  # fixed at current folder

### .logfile configuration file location    
logFile = ".logging"
LOG_NAME = "ServerMon"

### meta file 
META_FILE_NAME = ".2storeMeta"

### ignore file list 
ignoreFileList = []
ignoreFolderList = []

## init. the global variables, this function is called by main()      
##################################################
def init():
    
## Configuration file for different parameters
    global configFile
    configFile = ConfigParser.ConfigParser() 
    configFile.read(paraFile)
    
## Base Path for the owncloud folder 
    global basePath 
    basePath = os.path.normpath(configFile.get("default", "BASE_PATH"))
    
## fixed regular interval to operation, in second unit 
    global reg_period
    reg_period = float(configFile.get("default", "REG_PERIOD"))

## ignore file list 
    global ignoreFileList
    for ignorePattern in configFile.get("default", "IGNORE_FILE_LIST").split(','):
        ignoreFileList.append(ignorePattern.strip())

## ignore file list 
    global ignoreFolderList
    for ignorePattern in configFile.get("default", "IGNORE_FOLDER_LIST").split(','):
        ignoreFolderList.append(ignorePattern.strip())

def getBasePath():
    global basePath
    return basePath
    
def getConfigFile():
    global configFile
    return configFile

def getRegPeriod():
    global reg_period 
    return reg_period

def ignoreFileListMatch(fileName):
    global ignoreFileList 
    for thisPattern in ignoreFileList:
        if fnmatch.fnmatch(fileName, thisPattern):
            return True
    return False

def ignoreFolderListMatch(folderName):
    global ignoreFolderList 
    for thisPattern in ignoreFolderList:
        if fnmatch.fnmatch(folderName, thisPattern):
            return True
    return False
