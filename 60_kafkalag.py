#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：chenglinguang
#Date：2018.10.18
#Version：1.0
#V1.0 Description: kafka monitor

import os
import time
import commands
import subprocess
import json
import sys
import re
import urllib2
import platform
import logging
import re
import ConfigParser
endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
status = 1

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
        logging.error('exec: %s failed! err:%s' %(cmd,child.stdout.read()))
        return None
    else:
        return child.stdout.read()

def getkafkainfo():
        kafkapath = None
        kafkahost = None
	#切换目录
	try:
	    os.chdir(r'/home/work/open-falcon/conf')
	except Exception,e:
	    logging.error(str(e))
            status = 0
	    return None,None
	#判断配置文件是否存在
	if not os.path.exists(r'args.conf'):
	    logging.error('args.conf is not exists!')
            status = 0
            return None,None
	#获取参数值
	mysection = sys.argv[0].split('.')[0].split('_',1)[1]
	cf = ConfigParser.ConfigParser()
	cf.read(r'args.conf')
	if mysection not in cf.sections():
	    logging.error('Config section wrong!')
            status = 0
	    return None,None
        for item in cf.items(mysection):    
	    if item[0]=="path":
                kafkapath=item[1]
            if item[0]=="host":
                kafkahost=item[1]
        return kafkapath,kafkahost

def getkafkagroups(path,host):
    info = {}
    if os.path.exists(path):
        os.chdir(path)
    else:
        status = 0
        return None
    groups = run_command("bin/kafka-run-class.sh kafka.admin.ConsumerGroupCommand --bootstrap-server %s --list | grep -v CLASSPATH" %host,3)
    if groups is None:
        return None
    for group in groups.strip().split('\n'):
        group = group.strip()
        if re.match(r'[0-9]+',group) or 'test' in group:
            continue
        info[group]={}
        topicinfo = run_command("bin/kafka-run-class.sh kafka.admin.ConsumerGroupCommand --bootstrap-server %s --group %s --describe | grep -v CLASSPATH" %(host,group),3)
        if topicinfo is None:
            continue
        topicinfo = topicinfo.strip().split('\n')
        if "TOPIC" not in topicinfo[0]:
            continue
        topicindex = topicinfo[0].split().index("TOPIC")
        lagindex = topicinfo[0].split().index("LAG")
        for topicitem in topicinfo[1:]:
            topic=topicitem.split()[topicindex]
            lag=topicitem.split()[lagindex]
            if topic != "-" and lag != "-":
                if info[group].has_key(topic):
                    info[group][topic]+=int(lag)
                else:
                    info[group][topic]=int(lag)
    return info

if __name__ == "__main__":
    with open('/home/work/open-falcon/agent/cfg.json','r') as f:
        json_file=json.loads(f.read())
        endpoint=json_file['hostname']
    ts=int(time.time())
    step=60
    counter_list=[]
    path,host=getkafkainfo()
    if path is not None and host is not None:
        kafkainfo = getkafkagroups(path,host)
        for group in kafkainfo:
            for topic in kafkainfo[group]:
                counter_list.append({"endpoint":endpoint,"metric":"kafka.group.%s" %group,"tags":"topic=%s" %topic,"timestamp":ts,"step":step,"counterType":"GAUGE","value":kafkainfo[group][topic]})
                counter_list.append({"endpoint":endpoint,"metric":"kafka.consume.lag","tags":"group=%s,topic=%s" %(group,topic),"timestamp":ts,"step":step,"counterType":"GAUGE","value":kafkainfo[group][topic]})
    counter_list.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": ts, "step": step, "value": status, "counterType": "GAUGE", "tags": "scripts=60_kafkalag.py"}) 
    print json.dumps(counter_list)
