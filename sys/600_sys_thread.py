#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2016.12.04
#Version：1.0
#V1.0 Description：系统线程数监控

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
logging.basicConfig(level=logging.INFO,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

try:
    value=int(commands.getoutput("ps -eLf 2>/dev/null | wc -l").strip())
except Exception,err:
    logging.error("Run command failed:%s" %str(err))
    sys.exit(2)
def create_record():
    record = {}
    record['metric'] = 'sys.thread'
    record['endpoint'] = endpoint
    record['timestamp'] = ts
    record['step'] = 600
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()

data.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": 600, "value": status, "counterType": "GAUGE", "tags": "scripts=600_sys_thread.py"})
print json.dumps(data)
