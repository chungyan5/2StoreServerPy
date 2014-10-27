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
import shutil 

### configuration file parser library 
import ConfigParser

### global variables
import globalMod

### execute linux command 
import subprocess

## create logging
##################################################
serverModLogger = logging.getLogger('ServerMon.OffOnlineMode')

## this module variables 
##################################################

META_FILE_NAME = ".2storeMeta"

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
        #    TODO: remove the following warning
        for root, dirs, files in os.walk(globalMod.getBasePath()):
            #serverModLogger.debug('root %s', root)
            #for dir in dirs:
            #    serverModLogger.debug('dirs %s', dir)
            #for file in files:
            #    serverModLogger.debug('files %s', file)
            for filename in fnmatch.filter(files, '*' + META_FILE_NAME):
                
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
#######                 get a meta -> max. folder size
                        try: 
                            maxFolderSize = int(meta.get("default", "MAX_FOLDER_SIZE")) * 1024 * 1024   # change fr. ??G to ??k 

#######                 read the existing folder file size 
                            # reference from http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
                            existingFolderSize = int(subprocess.check_output(["du", "-s", root]).split()[0])        # return in ???k unit 
                            
#######                 if existing folder file size is ~80% of the meta -> max. folder size 
                            serverModLogger.debug( "compare %d and %d", existingFolderSize, (maxFolderSize*0.8))
                            if existingFolderSize >= (maxFolderSize*0.8):
                                
########                    locate the corresponding folder at pool (.../user/files/...) or create a new one  
                                serverModLogger.debug( "existingFolderSize larger %s", root)
                                path_list = root.split(os.sep)
                                i = path_list.index(globalMod.SYNC_DEVICES)
                                path_list.pop(i+1)
                                path_list.remove(globalMod.SYNC_DEVICES)
                                update_path = os.sep.join(path_list)
                                serverModLogger.debug( "update_path %s", update_path)

#########                       create this folder if not existing .../user/files/device.../...
                                try:
                                    statinfo = os.stat(root)
                                    os.makedirs(update_path, statinfo[0])
                                except OSError:
                                    os.chmod(update_path, statinfo[0])                  # change the mode same to original
                                
#########                       move this 50% older files to this new pool folder

                                # exclusive .2storeMeta
                                theseFiles = []
                                for f in os.listdir(root):
                                    if not fnmatch.fnmatch(f, META_FILE_NAME):
                                        theseFiles.append(os.path.join(root, f))
                                
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
                                    
                                    #sourceFile = os.path.join(root, fileName)
                                    #shutil.move(sourceFile, update_path)
                                    shutil.move(fileName, update_path)              # this function will mv file, soft-link and folder
                                    
                                    #serverModLogger.debug( "total_size %d ", total_size)
                                    #serverModLogger.debug( "maxFolderSize*0.5 %d ", maxFolderSize*0.5)
                                    if (total_size>maxFolderSize*0.5):
                                        break
                                   
#########                       create a new .meta file at pool new folder with online mode
                                # cp the existing meta file and modify it
                                serverModLogger.debug( "os.path.join(root, META_FILE_NAME) ", os.path.join(root, META_FILE_NAME))
                                shutil.copy(os.path.join(root, META_FILE_NAME), update_path)
                                newMeta = ConfigParser.SafeConfigParser()
                                newMetaFile = os.path.join(update_path, META_FILE_NAME)
                                newMeta.read(newMetaFile)
                                newMeta.set('default', 'ON_OFF_STATUS', '2')    # change to online mode
                                with open(newMetaFile, 'wb') as configfile:
                                    newMeta.write(configfile)
                        
#######                 it is not a folder, so skip 
                        except ConfigParser.NoOptionError:
                            pass
                        
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
                
                