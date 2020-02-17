#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2016.12.04
#Version：1.0
#V1.0 Description：corefile文件监控

from subprocess import Popen,PIPE
import os
import time
import re
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

def get_value(dir):
    os.system("mkdir {0}bak &>/dev/null".format(dir))
    if os.path.exists(dir):
        files = os.listdir(dir)
        if files:
            for file in files:
                if os.stat(dir+'/'+file).st_ctime < time.time()-86400:
                    os.system('mv {0}/{1} {2}bak/'.format(dir,file,dir))
        for file in os.listdir('{0}bak'.format(dir)):
            if os.stat(dir+'bak/'+file).st_ctime < time.time()-86400*7:
                os.remove('{0}bak/{1}'.format(dir,file))
        return len(os.listdir(dir))
    else:
        return 0

def create_record():
    record = {}
    record['metric'] = 'check.corefile'
    record['endpoint'] = endpoint
    record['timestamp'] = ts
    record['step'] = 600
    record['value'] = get_value('/home/corefile')+get_value('/var/corefile')+get_value('/var/jucloud/core')
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
data.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": 600, "value": status, "counterType": "GAUGE", "tags": "scripts=600_corefile.py"})
print json.dumps(data)
