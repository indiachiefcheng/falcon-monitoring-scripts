#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2018.04.15
#Version：1.0
#V1.0 Description: null

import os
import time
import json
import subprocess
import platform
import sys
import logging
import threading
status = 1
data=[]
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
    if (child.returncode != 0):
        logging.error('exec: %s failed!' %cmd)
        return None
    else:
        return child.stdout.readlines()

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

ts = int(time.time())
cmd = "systemctl --full --no-pager --no-legend list-units | wc -l"
res = run_command(cmd,10)
if res is not None:
    value = int(res[0])
else:
    status = 0 
    value = 999999

def create_record():
    record = {}
    record['metric'] = 'systemd.units'
    record['endpoint'] = endpoint
    record['timestamp'] = int(time.time())
    record['step'] = 300
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
data.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": 300, "value": status, "counterType": "GAUGE", "tags": "scripts=300_systemd_units.py"}) 
print json.dumps(data)
