'''
Filename: ServerMon.py
Description: Server Monitoring tasks
                1) starting the online and offline mode 
             Attention for running this script: must be run in superuser or www-data user daemon in linux platform only 
@author: yan, chungyan5@gmail.com, 2Store
Technical: Main() --(call to)-> 
                Daemon App Class --(call to)-> 
                    Daemon_App_Class.pyinotify_with_Event_Class
Testing Cases:
1) on 2014_11_01
    - create a new meta file
    - changing of meta file
'''

## import other libraries
##################################################

### daemon library 
from daemon import runner

### logging library 
import logging.config

### global variables
import globalMod

### inotify module in Ver 0.9.2 
import pyinotify

### file names matching library and file system searching 
import os

### Offline and Online Mode 
from OffOnlineMode import OffOnlineMode

class DaemonApp():
    
## inotify Events handling      
##################################################

    class EventHandler(pyinotify.ProcessEvent):
        
        def __init__(self, outer):
            self.outer = outer
            
## handling Events Common function       
##################################################
        def process_default(self, event):
            
            serverModLogger.debug('process_default %s %s', event.maskname, event.pathname)
            
            path, filename = os.path.split(event.pathname)
            
        ### is it .2storeMeta, Yes,
            if filename == globalMod.META_FILE_NAME:
                
                ### call handling manipulate .2storeMeta file function
                self.outer.offOnlineMode.handleMetaFile(path, filename)
        
        ### Not .2storeMeta, it should be any Folder(s)/File(s)
            elif globalMod.ignoreFileListMatch(filename):
                pass        # do nothing when match this ignore list
            else:
                self.outer.offOnlineMode.scanMetaFolderBottomUp(path)
                pass
        
## This Daemon Application      
##################################################

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'              # most of pyinotify err. msg can be changed to exception
        self.pidfile_path =  '/tmp/serverMod.pid'
        self.pidfile_timeout = 5
        
        self.offOnlineMode = OffOnlineMode()
        
    def run(self):
        
        serverModLogger.info('Start daemon running')
        
## inotify algorithm       
##################################################

### start pyinotify
        
        # Instanciate a new WatchManager (will be used to store watches).
        wm = pyinotify.WatchManager()
                       
        # watched events which specific tested for btsync
        #    ignore the events as following 
        #        IN_OPEN -- open to read by btsync 
        #        IN_CLOSE_NOWRITE -- after read the content and close without any modification 
        #        IN_ACCESS -- normal access the file/folder for reading 
        #        IN_ATTRIB -- changing attrib but we just care content changing 
        #        IN_MOVED_FROM -- rename from XXX to new one, we just handle IN_MOVED_To after completed the rename  
        #    should included events 
        #        IN_MOVED_TO -- from .2storeMeta.!sync to(this a new file name event) .2storeMeta
        #        IN_CLOSE_WRITE
        #        IN_DELETE_SELF
        #        IN_CREATE
        mask = pyinotify.ALL_EVENTS ^ pyinotify.IN_OPEN ^ pyinotify.IN_CLOSE_NOWRITE ^ \
                 pyinotify.IN_ACCESS ^ pyinotify.IN_ATTRIB ^ pyinotify.IN_MOVED_FROM
        #mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE_SELF | pyinotify.IN_CREATE
        
        # Associate this WatchManager with a Notifier (will be used to report and process events).
        notifier = pyinotify.Notifier(wm, DaemonApp.EventHandler(self))
        
        try:
            wm.add_watch(globalMod.getBasePath(), mask, quiet=False, rec=True, auto_add=True)
        except pyinotify.WatchManagerError, err:
            serverModLogger.error('Init. pyinotify Err. %s', err)
            
        # Loop forever and handle events.
        notifier.loop()
             
## start the Main Core Application    
#################################
if __name__ == '__main__':

## setup the global variables 
##################################################
    globalMod.init()

## logging setting 
##################################################
    logging.config.fileConfig(globalMod.logFile)
    serverModLogger = logging.getLogger('ServerMon')
    serverModLogger.info('===========================================')
    # TODO: display corresponding "start or stop" msg
    serverModLogger.info('Start info message from Main Server Monitor')

## call daemon library
##################################################
## This Class Server Monitor Daemon Content    
##################################################
    app = DaemonApp()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=[serverModLogger.handlers[0].stream]    # This ensures that the logger file handle does not get closed during daemonization
                                                                                        #    reference: http://stackoverflow.com/questions/4375669/logging-in-python-with-config-file-using-handlers-defined-in-file-through-code
    daemon_runner.do_action()
