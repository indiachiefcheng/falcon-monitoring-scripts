#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2016.12.04
#Version：1.0
#V1.0 Description：docker虚拟机CPU监控
import subprocess
import json
import time
import socket
import commands
import logging
import sys
import platform
import re
status = 1
data=[]
endpoint="default"
ts = int(time.time())
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

def create_record(value):
    record={}
    record['metric'] = 'docker.cpu'
    record['endpoint'] = endpoint
    record['timestamp'] = ts
    record['step'] = 300
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
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
cmd1 = "/usr/bin/sh /usr/local/fountain/docker/docker-tools_centos7.2/docker-monitor -c"
cmd2 = "/usr/bin/sh /home/work/open-falcon/agent/plugin/docker/docker-monitor -c"
version = int(''.join(platform.dist()[1].split('.')[0:2]))
if version > 71:
    re = run_command(cmd1,60)
else:
    re = run_command(cmd2,60)
try:
    value=float(re[1].split(':')[1].split()[0])
    create_record(value)
except Exception,err:
    status = 0
    logging.error("Run command failed:%s" %str(err))
data.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": 300, "value": status, "counterType": "GAUGE", "tags": "scripts=300_docker_cpu.py"})        
print json.dumps(data)
