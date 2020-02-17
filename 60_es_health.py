#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author :chenglinguang
#监控es集群的status,number_of_nodes,number_of_data_nodes,relocating_shards,initializing_shards,unassigned_shards,delayed_unassigned_shards
#监控es每个索引的status,异常是1，正常是0  Data：2019.10.09


import urllib2
import time
from urllib import urlencode
import json
import os
import sys
import time
import urllib2
import platform
import logging
import re
import commands
import ConfigParser
STATUS = 1
endpoint="default"
logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')



with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

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

cf = ConfigParser.ConfigParser()
cf.read(r'args.conf')
if 'esmonitor' not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
else:
    port=cf.get('esmonitor','port')

#es_health_code: 0,1 0 represent problem; 1 represent healthy
counter_list=[]
ts=int(time.time())
step=60

try:

    res = urllib2.urlopen('http://localhost:%s/_cluster/health?level=indices' %str(port),timeout=5)
    #res = urllib2.urlopen('http://localhost:%s/_cluster/health' %str(port),timeout=5)  
    res_dict = json.loads(res.read())
    status = res_dict.get('status')
    number_of_nodes = res_dict.get('number_of_nodes')
    number_of_data_nodes = res_dict.get('number_of_data_nodes')
    relocating_shards = res_dict.get('relocating_shards')
    initializing_shards = res_dict.get('initializing_shards')
    unassigned_shards = res_dict.get('unassigned_shards')
    delayed_unassigned_shards = res_dict.get('delayed_unassigned_shards')   
    #监控脚本查询es的请求是否执行成功
    es_health_geturl=1

    if status == "green" or status == "yellow":
        status=1
    else:
        status=0
    #发送监控脚本查询es的请求是否执行成功的结果，成功是1，失败是0
    counter_list.append({'endpoint': endpoint,'metric': 'es.health.geturl',"timestamp": ts, "step": step,"value": es_health_geturl, "counterType": "GAUGE", "tags": ""})
    #监控es集群的status,number_of_nodes,number_of_data_nodes,relocating_shards,initializing_shards,unassigned_shards,delayed_unassigned_shards的值
    counter_list.append({'endpoint':endpoint,'metric':'es.health.status',"timestamp": ts, "step": step,"value": status, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.number_of_nodes',"timestamp": ts, "step": step,"value": number_of_nodes, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.number_of_data_nodes',"timestamp": ts, "step": step,"value": number_of_data_nodes, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.relocating_shards',"timestamp": ts, "step": step,"value": relocating_shards, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.initializing_shards',"timestamp": ts, "step": step,"value": initializing_shards, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.unassigned_shards',"timestamp": ts, "step": step,"value": unassigned_shards, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.delayed_unassigned_shards',"timestamp": ts, "step": step,"value": delayed_unassigned_shards, "counterType": "GAUGE", "tags":""})
    #监控每个索引的状态
    indices = res_dict.get('indices')
    for key1,values1 in indices.items():
       tmp_tags = 'index=' + key1
       if  values1['status'] == 'red' or values1['status'] == 'yellow':
           counter_list.append({'endpoint': endpoint,'metric': "es.health.index_status","timestamp": ts, "step": step,"value": 1, "counterType": "GAUGE", "tags":tmp_tags})
       else:
           counter_list.append({'endpoint': endpoint,'metric': "es.health.index_status","timestamp": ts, "step": step,"value": 0, "counterType": "GAUGE", "tags":tmp_tags})

except:
    STATUS = 0
    es_health_geturl=0
    counter_list.append({'endpoint':endpoint,'metric':'es.health.geturl',"timestamp": ts, "step": step,"value": es_health_geturl, "counterType": "GAUGE", "tags":""})


counter_list.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": step, "value": STATUS, "counterType": "GAUGE", "tags": "scripts=60_es_health.py"})
print json.dumps(counter_list)







