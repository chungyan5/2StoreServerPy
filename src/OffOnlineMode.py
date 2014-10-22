'''
Filename: OffOnlineMode.py
Description: offline and online mode 
@author: yan, chungyan5@gmail.com, 2Store
'''

## import other libraries
##################################################

### logging library 
import logging

### file names matching library and file system searching 
import fnmatch
import os
#import scandir             # using scandir lib. instead of standard os due to more faster speed 

### configuration file parser library 
import ConfigParser

### global variables
import globalMod

### input this application global variable 
#from ServerMon import syncPath

## create logging
##################################################
serverModLogger = logging.getLogger('ServerMon.OffOnlineMode')

## this module class
##################################################
class OffOnlineMode(object):
    '''
    classdocs
    '''

    def __init__(self, user_base_path):
        '''
        Constructor
        '''
        self.user_base_path = user_base_path
        
## Main Execution 
##################################################
    def execution(self):

### monitoring the .meta
##################################################
        
####    scan each folders and files for .meta file at 
####        each location from .../owncloud/data/"user".../files/... folders AND
####        .../owncloud/data/"user".../files/Sync_Devices/... folders
        # TODO: may be a faster solution than os.walk()
        #    os.walk() -- no error in encoding, but slower
        #    scandir.walk() -- has error in encoding, but faster 
        #    may add a exception handling to skip this err. due to not my matching in .meta
        for root, dirs, files in os.walk(self.user_base_path):
            #serverModLogger.debug('root %s', root)
            #for dir in dirs:
            #    serverModLogger.debug('dirs %s', dir)
            #for file in files:
            #    serverModLogger.debug('files %s', file)
            for filename in fnmatch.filter(files, "*.2storeMeta"):
                
####    read each meta file (detect the 1st meta file only, then ignore all sub-folders meta file)
                # TODO: no verify the right format of "*.2storeMeta" file. if wrong format, just exception quit and broken this daemon 
                meta = ConfigParser.ConfigParser() 
                meta.read(os.path.join(root, filename))

#####        get meta -> ON_OFF_STATUS
                onOffStatus = meta.get("default", "ON_OFF_STATUS")
                
#####           if default offline
                if onOffStatus == "0":
######              if at Sync_devices folder 
                    if globalMod.SYNC_PATH in root:
                        serverModLogger.debug( os.path.join(root, filename) + " default offline at Sync_devices")
                        
######              if at pool folder 
                    else:
                        serverModLogger.debug( os.path.join(root, filename) + " default offline at pool")

#####           if offline
                elif onOffStatus == "1":
######              if at Sync_devices folder 
                    if globalMod.SYNC_PATH in root:
                        serverModLogger.debug( os.path.join(root, filename) + " offline at Sync_devices")
                        
######              if at pool folder 
                    else:
                        serverModLogger.debug( os.path.join(root, filename) + " offline at pool")
                    
#####           if online
                elif onOffStatus == "2":
######              if at Sync_devices folder 
                    if globalMod.SYNC_PATH in root:
                        serverModLogger.debug( os.path.join(root, filename) + " online at Sync_devices")
                        
######              if at pool folder 
                    else:
                        serverModLogger.debug( os.path.join(root, filename) + " online at pool")
                #else: TODO: adding err. handling in future   
                
                