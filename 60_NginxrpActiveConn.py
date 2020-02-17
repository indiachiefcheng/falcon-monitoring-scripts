#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2016.12.15
#Version：1.0
#V1.0 Description：nginx活跃连接数 usage:NginxrpActiveConn.py

import os
import time
import commands
import json
import sys
import re
import urllib2
import platform
import logging
import re
import ConfigParser
status = 1
endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']

#切换目录
try:
    os.chdir(r'/home/work/open-falcon/conf')
except Exception,e:
    logging.error(str(e))
    sys.exit(3)
#判断配置文件是否存在
if not os.path.exists(r'args.conf'):
    logging.error('args.conf is not exists!')
    sys.exit(4)
#获取参数值
mysection = sys.argv[0].split('.')[0].split('_',1)[1]
cf = ConfigParser.ConfigParser()
cf.read(r'args.conf')
if mysection not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
if len(cf.items(mysection))!=1:
    logging.error("Need only one ip!")

ip=cf.items(mysection)[0][1]
ts=int(time.time())
step=60
counter_list=[]
flag=0
out=commands.getoutput('curl http://%s/reverse-status' % ip)

for line in out.split('\n'):
    if re.search('Active connections',line):
        value=int(line.split(':')[1])
        flag=1
        counter_list.append({"endpoint":endpoint,"metric":"nginx.active_connections","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":value})    
    if re.search('Reading',line):
        counter_list.append({"endpoint":endpoint,"metric":"nginx.reading","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":int(line.split()[1])}) 
        counter_list.append({"endpoint":endpoint,"metric":"nginx.writing","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":int(line.split()[3])}) 
        counter_list.append({"endpoint":endpoint,"metric":"nginx.waiting","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":int(line.split()[5])}) 

if flag ==0:
   logging.error("Get nginx Active connections failed!")
   status = 0
counter_list.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": step, "value": status, "counterType": "GAUGE", "tags": "scripts=60_NginxrpActiveConn.py"})
print json.dumps(counter_list)
