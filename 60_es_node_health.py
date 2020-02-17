#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author :chenglinguang
#监控node的状态，1是正常 0是不正常
#监控脚本获取节点健康状态的url是否正常，1是不正常
#监控node节点的jvm的堆内存使用的百分比
#监控node节点的jvm的堆内存老年代gc的次数累计
#监控node节点的jvm的堆内存老年代gc的时间累计，单位是ms
#监控node节点自启动以来查询消耗的总时间和查询数量的比值，比值越大说明每个查询花费的时间越多
#监控node节点自启动以来的query和fetch耗时。Date：2019.9.1
#监控node节点的index当前运行着几个Lucene段合并(merges)。Date：2019.10.8


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
    #print (nodes_status_dict['failed']) 
    for key1, values1 in nodes_dict.items():
        tmp_tags1 = 'es_node=' + values1.get('host') + '_' + values1.get('name')
        for key2, values2 in values1['jvm'].items():
           if isinstance(values2, dict) and key2 == 'mem':
            counter_list.append({'endpoint': endpoint, 'metric': 'node_jvm_mem_heap_used_percent', "timestamp": ts, "step": step,"value": values2.get('heap_used_percent'), "counterType": "GAUGE", "tags": tmp_tags1})
           elif   isinstance(values2, dict) and key2 == 'gc':
                for key4, values4 in values2['collectors'].items():
                    if isinstance(values4, dict) and key4 == 'old':
                        counter_list.append({'endpoint': endpoint, 'metric': 'node_jvm_gc_old_collection_count', "timestamp": ts,"step": step,"value": values4.get('collection_count'), "counterType": "GAUGE", "tags": tmp_tags1})
                        counter_list.append({'endpoint': endpoint, 'metric': 'node_jvm_gc_old_collection_time_in_millis', "timestamp": ts,"step": step,"value": values4.get('collection_time_in_millis'), "counterType": "GAUGE", "tags": tmp_tags1})             
        #轮询indices
        for key5, values5 in values1['indices'].items():
            #print values5
            # 找到search
            if isinstance(values5, dict) and key5 == 'search':
                # 发送query_time_in_millis/query_total的值--自启动以来查询平均耗时
                counter_list.append({'endpoint': endpoint, 'metric': 'query_time_in_millis/query_total', "timestamp": ts, "step": step, "value": values5.get('query_time_in_millis') / float(values5.get('query_total')),"counterType": "GAUGE", "tags": tmp_tags1})
                #发送query_time_in_millis
                counter_list.append({'endpoint': endpoint, 'metric': 'query_time_in_millis', "timestamp": ts, "step": step, "value": values5.get('query_time_in_millis'),"counterType": "GAUGE", "tags": tmp_tags1})
                #发送fetch_time_in_millis
                counter_list.append({'endpoint': endpoint, 'metric': 'fetch_time_in_millis', "timestamp": ts, "step": step, "value": values5.get('fetch_time_in_millis'),"counterType": "GAUGE", "tags": tmp_tags1})
            #找到merges
            if isinstance(values5, dict) and key5 == 'merges':
                counter_list.append({'endpoint': endpoint, 'metric': 'merges_current', "timestamp": ts, "step": step, "value": values5.get('current'),"counterType": "GAUGE", "tags": tmp_tags1})


except:
    pass    

counter_list.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": step, "value": status, "counterType": "GAUGE", "tags": "scripts=60_es_node_health.py"})
print json.dumps(counter_list)
