'''
Filename: ServerMon.py
Description: Server Monitoring tasks
                1) starting the online and offline mode 
             Attention for running this script: must be run in superuser or www-data user daemon
@author: yan, chungyan5@gmail.com, 2Store
Technical: Main() --(call to)-> 
                Daemon App Class --(call to)-> 
                    Daemon_App_Class.pyinotify_with_Event_Class 
'''

## import other libraries
##################################################

### daemon library 
from daemon import runner

### logging library 
import logging.config

### global variables
import globalMod

### inotify module 
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
        def whenEventsOccur(self, event):
            
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
        
        def process_IN_CLOSE_WRITE(self, event):
            
            #serverModLogger.debug('IN_CLOSE_WRITE')
            
            self.whenEventsOccur(event)
            
        def process_IN_CREATE(self, event):
            
            serverModLogger.debug('IN_CREATE %s', event.pathname)
                
            self.whenEventsOccur(event)
        
        def process_IN_DELETE_SELF(self, event):
            
            serverModLogger.debug('IN_DELETE_SELF %s', event.pathname)
                
            self.whenEventsOccur(event)
        
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
        # watched events
        mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE_SELF | pyinotify.IN_CREATE
        # Associate this WatchManager with a Notifier (will be used to report and process events).
        handler = DaemonApp.EventHandler(self)
        notifier = pyinotify.Notifier(wm, handler)
        
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
