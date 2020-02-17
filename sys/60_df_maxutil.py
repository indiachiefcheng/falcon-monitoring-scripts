#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2017.05.17
#Version：1.0
#V1.0 Description:监控分区磁盘使用率及inodes使用率，取使用率最高的值 

import os
import sys
import time
import json
import commands
import urllib2
import platform
import logging
import re
import subprocess
status = 1
endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

def run_command(cmd,timeout):
    start_time = time.time()
    child = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while child.poll() is None:
        time.sleep(0.2)
        now_time=time.time()
        if (now_time-start_time) > timeout:
            child.kill()
            logging.error("exec: %s timeout!"  %cmd)
            return None
    return child.stdout.readlines()

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

counter_list=[]
ts=int(time.time())
step=60
df_disk_list = run_command('df -l -x iso9660 -h',10)
df_inodes_list = run_command('df -l -x iso9660 -i',10)
df_disk_maxutil=0
df_inodes_maxutil=0
try:
    for item in df_disk_list[1:] :
        if '/etc/hosts' not in item.split()[5] and 'loop' not in item.split()[0] and '/mnt' not in item.split()[5]:
            if int(item.split()[4].split('%')[0]) > df_disk_maxutil:
                df_disk_maxutil = int(item.split()[4].split('%')[0])

    for item in df_inodes_list[1:]:
            if '-' not in item.split()[4] and 'loop' not in item.split()[0] and '/etc/hosts' not in item.split()[5] and '/mnt' not in item.split()[5]:
                if int(item.split()[4].split('%')[0]) > df_inodes_maxutil:
                    df_inodes_maxutil = int(item.split()[4].split('%')[0])

except Exception,err:
    logging.error("Get value failed, %s" %str(err))
    sys.exit(3)
counter_list.append({"endpoint":endpoint,"metric":"df.disk.maxutil","timestamp": ts, "step": step,"value": df_disk_maxutil, "counterType": "GAUGE", "tags":""})
counter_list.append({"endpoint":endpoint,'metric':"df.inodes.maxutil","timestamp": ts, "step": step,"value": df_inodes_maxutil, "counterType": "GAUGE", "tags":""})
counter_list.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": step, "value": status, "counterType": "GAUGE", "tags": "scripts=60_df_maxutil.py"}) 
print json.dumps(counter_list)
