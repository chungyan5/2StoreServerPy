#!/usr/bin/python
# Filename: ServerMon.py
# Description: Server Monitoring tasks
#                1) auto. Change from offline to online mode after meet a 90% full 
# Attention for running this script: must be run in superuser or www-data user by Cron regularly 
# Author: yan, chungyan5@gmail.com, 2Store   
##################################################

## import other libraries
### daemon time 
import time
### daemon library 
import daemon

## This Class Server Monitor Deamon   
##################################################
def do_main_program():
    cnt = 0 
    while True: 
        with open("/tmp/test1.txt", "a") as text1_file:
            text1_file.write("Cnt: {}\n".format(cnt))
            cnt = cnt +1
        time.sleep(5)

## call daemon library
##################################################
with daemon.DaemonContext():
    do_main_program()
