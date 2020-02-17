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
import urllib2
import sys
import logging

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

def get_redis_pid():
    redis_pids = {}
    cmd = "ps -ef | egrep 'redis-server|codis-server' | grep -v grep | awk '{print $2,$NF}' 2>/dev/null"
    res = run_command(cmd,10)
    if res is None:
        return redis_pids
    for line in res:
        redis_pids[line.split()[1].split(':')[1].strip()] = line.split()[0].strip()
    return redis_pids

def get_redis_bind_cpus(pid):
    cpus = ''
    cmd = "taskset -c -p {} 2>/dev/null".format(pid)
    res = run_command(cmd,10)
    if res is None:
        return cpus
    cpus_info = res[0].split(':')[-1].strip()
    for cpu in cpus_info.split(','):
        if '-' in cpu:
            for i in range(int(cpu.split('-')[0]),int(cpu.split('-')[1])+1):
                cpus = cpus + str(i) + ','
        else:
            cpus = cpus + cpu + ','
    return cpus.strip(',')

def get_redis_cpu_utils(cpus):
    value = 0.0
    len_cpus = len(cpus.split(','))
    cmd = "mpstat -P {} 1 5".format(cpus)
    res = run_command(cmd,10)
    if res is not None:
        for line in res:
            if line.startswith('Average:'):
                value = value + 100.0 - float(line.split()[-1])
    return value/len_cpus

def create_record(port,value):
    record = {}
    record['metric'] = 'redis.cpu.util'
    record['endpoint'] = endpoint
    record['timestamp'] = int(time.time())
    record['step'] = 60
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = 'port={}'.format(port)
    return record

if __name__ == '__main__':
    data=[]
    endpoint="default"
    status = 1
    with open('/home/work/open-falcon/agent/cfg.json','r') as f:
        json_file=json.loads(f.read())
        endpoint=json_file['hostname']
    ip=endpoint.split('_')[0]
    redis_pids = get_redis_pid()
    for port in redis_pids:
        cpus = get_redis_bind_cpus(redis_pids[port])
        value = get_redis_cpu_utils(cpus)
        data.append(create_record(port,value))
    data.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": int(time.time()), "step": 60, "value": 1, "counterType": "GAUGE", "tags": "scripts=60_redis_cpu_util.py"})
    print json.dumps(data)

