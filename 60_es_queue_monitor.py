#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:chenglinguang
#由于node节点的线程池队列有时候需要非常高的频率执行，所以单独把它放到了一个脚本里了。
#监控node的状态，1是正常 0是不正常
#监控脚本获取节点健康状态的url是否正常，1是不正常
#监控node节点线程池的index，get，search，bulk队列的长度，
#监控es集群的任务队列最大等待时间，单位是ms



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
status = 1
endpoint = "default"
logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json', 'r') as f:
    json_file = json.loads(f.read())
    endpoint = json_file['hostname']
ip = endpoint.split('_')[0]

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

# es_node_health_code: 0,1 0 represent problem; 1 represent healthy
counter_list = []
ts = int(time.time())
step = 60

try:

    res = urllib2.urlopen('http://localhost:%s/_nodes/stats' %str(port), timeout=5)
    res_dict = json.loads(res.read())
    nodes_dict = res_dict.get('nodes')
    nodes_status_dict = res_dict.get('_nodes')
    for key1, values1 in nodes_dict.items():
        tmp_tags1 = 'es_node=' + values1.get('host') + '_' + values1.get('name')
        for key3, values3 in values1['thread_pool'].items():
            if isinstance(values3, dict) and key3 == 'index':
                 counter_list.append(
                {'endpoint': endpoint, 'metric': 'node_thread_pool_index_queue', "timestamp": ts, "step": step,"value": values3.get('queue'), "counterType": "GAUGE", "tags": tmp_tags1})
            elif isinstance(values3, dict) and key3 == 'get':
                 counter_list.append({'endpoint': endpoint, 'metric': 'node_thread_pool_get_queue', "timestamp": ts, "step": step,"value": values3.get('queue'), "counterType": "GAUGE", "tags": tmp_tags1})
            elif isinstance(values3, dict) and key3 == 'search':
                 counter_list.append({'endpoint': endpoint, 'metric': 'node_thread_pool_search_queue', "timestamp": ts, "step": step,"value": values3.get('queue'), "counterType": "GAUGE", "tags": tmp_tags1})
            elif isinstance(values3, dict) and key3 == 'bulk':
                 counter_list.append({'endpoint': endpoint, 'metric': 'node_thread_pool_bulk_queue', "timestamp": ts, "step": step,"value": values3.get('queue'), "counterType": "GAUGE", "tags": tmp_tags1})

except:
    status = 0
    pass

try:

    res = urllib2.urlopen('http://localhost:%s/_cluster/health' %str(port), timeout=5)
    res_dict = json.loads(res.read())
    max_wait = res_dict.get('task_max_waiting_in_queue_millis')
    counter_list.append({'endpoint': endpoint, 'metric': 'es_node_queue_wait', "timestamp": ts, "step": step, "value": max_wait,"counterType": "GAUGE", "tags": ""})

except:
    status = 0
    pass
counter_list.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": step, "value": status, "counterType": "GAUGE", "tags": "scripts=60_es_queue_monitor.py"})
print json.dumps(counter_list)
