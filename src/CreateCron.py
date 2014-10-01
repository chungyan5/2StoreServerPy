#!/usr/bin/python
# Filename: CreateCron.py
# Description: create a cron job 
# Attention for running this script: must be run in superuser or www-data user
# Author: yan, chungyan5@gmail.com, 2Store   
##################################################

## import other libraries
import argparse  
import ConfigParser
from crontab import CronTab             # using python_crontab lib.

## get optional arguments   
#################################
parser = argparse.ArgumentParser(description='Creating Cron Job')
parser.add_argument('-p', type=str, 
                   help='the config files path (.para)')
args = parser.parse_args()
if args.p == None:
    paraFile = ".para"                  # at current folder
else:
    paraFile = args.p + ".para"

## setup Configuration file for different parameters  
#################################

## prepare Configuration file
config = ConfigParser.ConfigParser() 
config.read(paraFile) 
cron_job_cmd = config.get("default", "REG_PROCESS")
regular_min = config.getint("default", "REG_PERIOD")

## setup Cron 
#################################
   
## prepare Cron job
easyStoreCronName = "2StoreCron"
user_cron = CronTab(user='www-data')

## check the existing cron job  
existingCron = user_cron.find_comment(easyStoreCronName)
try:
    existingCron.next()
    print "One 2Store cron job already installed"
except StopIteration:
    
## create a new cron job 
    print "NO right 2Store cron job, create a new now"
    newCron = user_cron.new(command=cron_job_cmd, comment=easyStoreCronName)
    newCron.minute.every(regular_min)     # cannot every(1), do not know why 
    user_cron.write_to_user()