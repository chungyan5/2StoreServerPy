'''
Created on Sep 12, 2014
Filename: AutoOff2Online.py
Description: auto. Change from offline to online mode after meet a 90% full
@author: yan, chungyan5@gmail.com, 2Store
'''

## import other libraries
##################################################
import scandir             # using scandir lib. instead of standard os due to more faster speed 

## config. this module as utf-8 encoding
##################################################
#import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

## this module class
##################################################
class AutoOff2Online():

    def __init__(self, user_base_path, syncPath, logger):
        self.user_base_path = user_base_path
        self.syncPath = syncPath
        self.logger = logger
        
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
            self.logger.debug('dirName: %s', curDir)
            j = j-1
            if j==0:
                break
            for fileName in fileList:
                self.logger.debug('fileName: %s ', fileName)
                if fileName == ".meta":
                    self.logger.debug('find out the %s at %s', fileName, curDir)
                    break
            for subDirName in subdirList:
                self.logger.debug('subDirName: %s ', subDirName)

## Auto. Offline to Online operation 
##################################################
    def off2Online(self):
        users = self.getAllUsersOneByOne()
        for user in users:
            self.logger.info('handling User: %s', user)
            thisUserPath = self.user_base_path + user + self.syncPath
            devices = self.getAllDevicesOneByOne(thisUserPath)
            for device in devices:
                self.logger.info('handling Device: %s', device)
                thisUserDevicePath = thisUserPath + device 
                self.seekMeta(thisUserDevicePath)
                
