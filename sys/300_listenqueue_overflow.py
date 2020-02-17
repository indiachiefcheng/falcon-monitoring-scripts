#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2017.07.22
#Version：1.0
#V1.0 Description：监控收到三次握手ack包，accept队列满
#from subprocess import Popen,PIPE
import os
import time
import json
import commands
import platform
import sys
import logging
status = 1
data=[]
endpoint="default"
ts = int(time.time())
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

try:
    result = commands.getoutput("netstat -s | grep overflow |awk '{print $1}'")
    if result=='':
        value=0
    else:
        value=int(result)
except Exception,err:
    logging.error("run command error")
    sys.exit(2)   
def create_record():
    record = {}
    record['metric'] = 'listenqueue.overflow'
    record['endpoint'] = endpoint
    record['timestamp'] = ts
    record['step'] = 300
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
data.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": 300, "value": status, "counterType": "GAUGE", "tags": "scripts=300_listenqueue_overflow.py"})
print json.dumps(data)
