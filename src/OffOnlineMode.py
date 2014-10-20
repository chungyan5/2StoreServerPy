'''
Created on Sep 12, 2014
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
import scandir             # using scandir lib. instead of standard os due to more faster speed 

## create logging
##################################################
serverModLogger = logging.getLogger('ServerMon.OffOnlineMode')

## this module class
##################################################
class OffOnlineMode():

    def __init__(self, user_base_path, syncPath):
        self.user_base_path = user_base_path
        self.syncPath = syncPath
        
## list all users one by one starting from .../owncloud/data/user.../ folder
##################################################
    def getAllUsersOneByOne(self):
        dirs = scandir.walk(self.user_base_path).next()[1]       # call 1st next(), i.e. the top folder; [1] as listing folder name only
        for eachDirName in dirs:     
            yield eachDirName

## list all devices starting from .../owncloud/data/user.../files/Sync_Devices/ folder
##################################################
    def getAllDevicesOneByOne(self, thisUserPath): 
        dirs = scandir.walk(thisUserPath).next()[1]
        for eachDirName in dirs:
            yield eachDirName

## looping to read each meta file for all devices
##################################################
    def seekMeta(self, thisUserDevicePath): 
        rootLoopingPath = thisUserDevicePath
        j = 5
        for curDir, subdirList, fileList in scandir.walk(rootLoopingPath):
            #self.logger.debug('dirName: %s', curDir)
            j = j-1
            if j==0:
                break
            for fileName in fileList:
                #self.logger.debug('fileName: %s ', fileName)
                if fileName == ".meta":
                    #self.logger.debug('find out the %s at %s', fileName, curDir)
                    break
            for subDirName in subdirList:
                serverModLogger.debug('subDirName: %s ', subDirName)

## Auto. Offline to Online operation 
##################################################
    def off2Online(self):
        users = self.getAllUsersOneByOne()
        for user in users:
            #self.logger.info('handling User: %s', user)
            thisUserPath = self.user_base_path + user + self.syncPath
            devices = self.getAllDevicesOneByOne(thisUserPath)
            for device in devices:
                #self.logger.info('handling Device: %s', device)
                thisUserDevicePath = thisUserPath + device 
                #self.seekMeta(thisUserDevicePath)
                
## Main Execution 
##################################################
    def execution(self):

### monitoring the .meta
##################################################
        
####    scan each folders and files for .meta file at 
####        each location from .../owncloud/data/"user".../files/... folders AND
####        .../owncloud/data/"user".../files/Sync_Devices/... folders 
        for root, dirs, files in os.walk(self.user_base_path):
            #serverModLogger.debug('root %s', root)
            #for dir in dirs:
            #    serverModLogger.debug('dirs %s', dir)
            #for file in files:
            #    serverModLogger.debug('files %s', file)
            for filename in fnmatch.filter(files, ".meta"):
                serverModLogger.debug( os.path.join(root, filename))
