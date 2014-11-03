'''
Filename: OffOnlineMode.py
Description: offline and online mode 
                1) auto. Change from offline to online mode after meet a 90% full
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
import shutil 

### configuration file parser library 
import ConfigParser

### global variables
import globalMod

### execute linux command 
import subprocess

### error handling 
import errno

## create logging
##################################################
serverModLogger = logging.getLogger('ServerMon.OffOnlineMode')

## this module variables 
##################################################

## this module class
##################################################
class OffOnlineMode(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

## find the corresponding Pool folder (.../user/files/...) from Sync device folder
## syncDeviceFolder -- sync device folder path
## return the path at pool
##################################################
    def findCorrPoolFolder(self, syncDeviceFolder):
        path_list = syncDeviceFolder.split(os.sep)
        i = path_list.index(globalMod.SYNC_DEVICES)
        path_list.pop(i+1)
        path_list.remove(globalMod.SYNC_DEVICES)
        return os.sep.join(path_list)
    
## Description: move data from src to dest
##    - avoiding overwrite file, just skip this moving process
##        eg. mv src/sameFileName dest/sameFileName 
##                or mv src/fileName dest/anotherFileName 
##                or mv src/fileName dest/anotherFolder where dest/anotherFolder contains sameFileName (dest/anotherFolder/sameFileName)
##            i.e. keep all of them in src/sameFileName, dest/sameFileName, dest/anotherFileName and dest/anotherFolder/sameFileName
##            AVOID: standard posix will overwrite the dest/sameFileName or dest/anotherFileName or dest/anotherFolder/sameFileName by src/fileName
##    - if same folder name(src/oneFolder and dest/oneFolder), move files inside src folder one by one
##        eg. mv src/oneFolder dest/oneFolder, 
##            i.e. mv src/oneFolder/* to dest/oneFolder/*
##            AVOID: standard posix will mv src/oneFolder to dest/oneFolder/oneFolder
## Testing Cases:
##    - move src/fileName and dest/fileName
##        * move src/sameFileName and dest/sameFileName; skip standard process and do nothing
##        * move src/fileName and dest/anotherFileName; skip standard process and do nothing
##    - move src/folderName and dest/fileName; standard process will raise err and do nothing
##    - move src/fileName and dest/folderName; skip standard process and chk dest/folderName/content  
##    - move src/folderName and dest/folderName 
##        * move src/sameFolderName and dest/sameFolderName; skip standard process and merge both Folders content into dest/sameFolderName 
##        * move src/folderName and dest/anotherFolderName; standard process, rise err and do nothing when dest/folderName/subFolderName same to srcFolderName 
## pseudo code:
##    if both are files, do nothing 
##    else if src is file and dest is folder
##        list dest content
##        if have same file name by scanning, do nothing 
##        if do not have same file name after scanning, do moving
##    else if both are folders and same name
##        list src content
##        one by one of src content to call this function again as file/folder to folder
##        if src folder is empty, remove it
##    else standard process
##        catch the exceptional errors, then skip them
##################################################
    def mvData(self, srcPath, destPath):
    
        # get full path src file/folder and dest file/folder   
        sDirFlag = os.path.isdir(srcPath)           # get file or folder attribute 
        dDirFlag = os.path.isdir(destPath)
        srcName = os.path.basename(srcPath)         # remove path and get base name only
        destName = os.path.basename(destPath)   
        
        # /srcFileName and /destFileName
        if (sDirFlag | dDirFlag) == 0:
            serverModLogger.debug("both as files %s %s", srcPath, destPath)
            
            # do nothing
            pass                  
        
        # /srcFileName and /destFolderName
        elif (sDirFlag==0) & (dDirFlag==1):
            serverModLogger.debug("/srcFileName and /destFolderName %s %s", srcPath, destPath)
            
            # list dest content
            for destSubFileFolderName in os.listdir(destPath):
                serverModLogger.debug("%s at list dest dir %s", destSubFileFolderName, destPath)
                
            # if have same file name(/srcFileName == /destFolderName/destSubFileOrFolderName), do nothing
                serverModLogger.debug("destFileFolderName %s and srcName %s", destSubFileFolderName, srcName)
                if fnmatch.fnmatch(destSubFileFolderName, srcName):
                    serverModLogger.debug("/srcFileName == /destFolderName/destSubFileOrFolderName, so do nothing")
                    return
                
            # if do not have same file name after scanning, do moving
            serverModLogger.debug("shutil.move(%s, %s)", srcPath, destPath)
            shutil.move(srcPath, destPath)              # this function will mv file, soft-link

        # /sameSrcFolderName == /sameDestFolderName
        elif (sDirFlag & dDirFlag) & (srcName == destName):
            serverModLogger.debug("/sameSrcFolderName == /sameDestFolderName %s %s", srcPath, destPath)
             
            # list src content 
            for srcSubFileFolderName in os.listdir(srcPath):
                serverModLogger.debug("%s at list src dir %s %s", srcSubFileFolderName, srcPath, destPath)
                
                # one by one of src content to call this function again as file/folder to folder
                self.mvData(os.path.join(srcPath, srcSubFileFolderName), destPath)

            # all others are using standard process
            try:
                os.rmdir(srcPath)
            except OSError as ose:
                if ose.errno == errno.ENOTEMPTY:
                    serverModLogger.debug("cannot remove %s due to directory not empty", srcPath)

        # all others are using standard process
        else:
            try:
                shutil.move(srcPath, destPath)
            except OSError as ose:
                serverModLogger.debug("OSError %s", ose)
            except shutil.Error as shutilErr:
                serverModLogger.debug("Error in dest/folderName/subFolderName same to srcFolderName: %s", shutilErr)

## Handle meta file  
##################################################
    def handleMetaFile(self, thisFolder, thisMetaFileName):

        ### read each meta file (detect the 1st meta file only, then ignore all sub-folders meta file)
        # TODO: no verify the right format of "*.2storeMeta" file. if wrong format, just exception quit and broken this daemon 
        meta = ConfigParser.ConfigParser() 
        meta.read(os.path.join(thisFolder, thisMetaFileName))
        serverModLogger.debug("os.path.join(thisFolder, thisMetaFileName) as %s", os.path.join(thisFolder, thisMetaFileName))

        #### get meta -> ON_OFF_STATUS
        onOffStatus = meta.get("default", "ON_OFF_STATUS")
        
        ####           if default offline
        if onOffStatus == "0":
        #####              if at Sync_devices folder 
            if globalMod.SYNC_PATH in thisFolder:
                serverModLogger.debug( os.path.join(thisFolder, thisMetaFileName) + " default offline at Sync_devices")
        ######                 get a meta -> max. folder size
                try: 
                    maxFolderSize = int(meta.get("default", "MAX_FOLDER_SIZE")) * 1024 * 1024   # change fr. ??G to ??k 

        ######                 read the existing folder file size 
                    # reference from http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
                    existingFolderSize = int(subprocess.check_output(["du", "-s", thisFolder]).split()[0])        # return in ???k unit 
                    
        ######                 if existing folder file size is ~80% of the meta -> max. folder size 
                    serverModLogger.debug( "compare %d and %d", existingFolderSize, (maxFolderSize*0.8))
                    if existingFolderSize >= (maxFolderSize*0.8):
                        
        #######                    locate the corresponding folder at pool (.../user/files/...) or create a new one  
                        serverModLogger.debug( "existingFolderSize larger %s", thisFolder)
                        
                        update_path = self.findCorrPoolFolder(thisFolder)
                        
                        serverModLogger.debug( "update_path %s", update_path)

        ########                       create this folder if not existing .../user/files/device.../...
                        try:
                            statinfo = os.stat(thisFolder)
                            os.makedirs(update_path, statinfo[0])
                        except OSError:
                            os.chmod(update_path, statinfo[0])                  # change the mode same to original
                        
        ########                       move this 50% older files to this new pool folder

                        # exclusive .2storeMeta
                        theseFiles = []
                        for f in os.listdir(thisFolder):
                            if not fnmatch.fnmatch(f, globalMod.META_FILE_NAME):
                                theseFiles.append(os.path.join(thisFolder, f))
                        
                        try:
                            thisSortedFiles = sorted(theseFiles, key=os.path.getmtime)
                        except Exception as e:
                            serverModLogger.debug( "exception %s", e)
                            
                        total_size = 0
                        for fileName in thisSortedFiles:
                            
                            # check accumulated file size 
                            #    chk link
                            #        chk folder
                            #            then file
                            if (os.path.islink(fileName)):
                                thisFileSize = os.path.getsize(fileName) /1024          # in XXXkbyte
                            elif os.path.isdir(fileName):                               # return TURE for both folder and soft-link
                                thisFileSize = int(subprocess.check_output(["du", "-s", fileName]).split()[0])  # return in XXXkbyte
                            else:
                                thisFileSize = os.path.getsize(fileName) /1024          # in XXXkbyte
                            total_size += thisFileSize
                            
                            self.mvData(fileName, update_path)
                            
                            #serverModLogger.debug( "total_size %d ", total_size)
                            #serverModLogger.debug( "maxFolderSize*0.5 %d ", maxFolderSize*0.5)
                            if (total_size>maxFolderSize*0.5):
                                break
                           
        ########                       create a new .meta file at pool new folder with online mode
                        # cp the existing meta file and modify it
                        serverModLogger.debug( "os.path.join(thisFolder, META_FILE_NAME) ", os.path.join(thisFolder, globalMod.META_FILE_NAME))
                        shutil.copy(os.path.join(thisFolder, globalMod.META_FILE_NAME), update_path)
                        newMeta = ConfigParser.SafeConfigParser()
                        newMetaFile = os.path.join(update_path, globalMod.META_FILE_NAME)
                        newMeta.read(newMetaFile)
                        newMeta.set('default', 'ON_OFF_STATUS', '2')    # change to online mode
                        with open(newMetaFile, 'wb') as configfile:
                            newMeta.write(configfile)
                
        ######                 it is not a folder, so skip 
                except ConfigParser.NoOptionError:
                    pass
                
        #####              if at pool folder 
            else:
                serverModLogger.debug( os.path.join(thisFolder, thisMetaFileName) + " default offline at pool")

        ####           if offline
        elif onOffStatus == "1":
        #####              if at Sync_devices folder 
            if globalMod.SYNC_PATH in thisFolder:
                serverModLogger.debug( os.path.join(thisFolder, thisMetaFileName) + " offline at Sync_devices")
                
        #####              if at pool folder 
            else:
                serverModLogger.debug( os.path.join(thisFolder, thisMetaFileName) + " offline at pool")
            
        ####           if online
        elif onOffStatus == "2":
        #####              if at Sync_devices folder 
            if globalMod.SYNC_PATH in thisFolder:
                serverModLogger.debug( os.path.join(thisFolder, thisMetaFileName) + " online at Sync_devices")
                
                # locate the corresponding folder at pool (.../user/files/...) XXXor create a new oneXXX
                update_path = self.findCorrPoolFolder(thisFolder)
                #statinfo = os.stat(thisFolder)
                
                # move files to this new pool folder
                serverModLogger.debug( "thisFolder %s", thisFolder)
                serverModLogger.debug( "update_path %s", update_path)

                # moving files
                self.mvData(thisFolder, update_path)
                # TODO: change the new created folder permission  
                #for root, dirs, files in os.walk(update_path, topdown=False):
                #    for dir in dirs:
                #        os.chmod(dir, statinfo[0])
                #    for file in files:
                #        os.chmod(file, statinfo[0])                
                
        #####              if at pool folder 
            else:
                serverModLogger.debug( os.path.join(thisFolder, thisMetaFileName) + " online at pool")
        #else: TODO: adding err. handling in future   
        
## Scan meta file corresponding folder and its recursive sub-folders (top-down) 
##################################################
    def scanMetaFolderTopDown(self, folder):

### monitoring the .meta
##################################################
        
####    scan each folders and files for .meta file at 
####        each location from .../owncloud/data/"user".../files/... folders AND
####        .../owncloud/data/"user".../files/Sync_Devices/... folders
        # TODO: may be a faster solution than os.walk()
        #    os.walk() -- no error in encoding, but slower
        #    scandir.walk() -- has error in encoding, but faster 
        #    may add a exception handling to skip this err. due to not my matching in .meta
        #    TODO: remove the following warning
        serverModLogger.debug("base folder fr. Top down as %s", folder)
        for curWalkingDirName, subdirList, fileList in os.walk(folder):
            #serverModLogger.debug('curWalkingDirName %s', curWalkingDirName)
            #for dir in subdirList:
            #    serverModLogger.debug('subdirList %s', dir)
            #for file in fileList:
            #    serverModLogger.debug('fileList %s', file)
            # TODO: only one .2storeMeta need to handle, ignore the sub-folder .2storeMeta 
            #        and XXX_FILE.2storeMeta, so should not use the following for loop 
            for filename in fnmatch.filter(fileList, '*' + globalMod.META_FILE_NAME):
                self.handleMetaFile(curWalkingDirName, filename)

## Scan meta file corresponding folder and its recursive sub-folders (buttom-up) 
##################################################
    def scanMetaFolderBottomUp(self, folder):
        
        curWalkingDirName = folder
        while True:
            
            ### ignore these folders
            if globalMod.ignoreFolderListMatch(os.path.basename(curWalkingDirName)):
                return
            
            serverModLogger.debug("base folder fr. bottom up as %s", curWalkingDirName)
            
            try:
                
            ### open this folder content
                fileList = os.listdir(curWalkingDirName)
            #### TODO: only one .2storeMeta need to handle, ignore the sub-folder .2storeMeta 
            ####        and XXX_FILE.2storeMeta, so should not use the following for loop 
            
            ### No such file or directory
            except OSError as ose:
                serverModLogger.debug("scanMetaFolderBottomUp Err as %s", ose)
            else:
                    
                ### seek the meta file current folder
                for filename in fnmatch.filter(fileList, '*' + globalMod.META_FILE_NAME):
                       
                ### if find the meta file, do something and break this loop
                    self.handleMetaFile(curWalkingDirName, filename)
                    return 
                 
            ### if already at upper level arrive, exit this loop
                if curWalkingDirName == globalMod.getBasePath():
                    return
            
            ### go to upper folder 
            curWalkingDirName = os.path.abspath(os.path.join(curWalkingDirName, os.pardir))
            