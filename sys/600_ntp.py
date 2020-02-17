#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import json
import os
import time
import logging

endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]


def fetch_ntp_state():

    # fail    获取状态: 0 获取成功, 1 获取失败
    # offset  ntp同步的偏移量, 使用绝对值表示
    # timeout 超时状态: 0 成功,     1 超时
    offset, fail, timeout = 0, 1, 0

    try:
        raw_data = Popen(['ntpq', '-pn'], stdout=PIPE, stderr=PIPE).communicate()[0]
        for line in raw_data.splitlines():
            if line.startswith('*'):
                l = line.split()
                when, poll, offset = l[4], l[5], l[8]

                offset          = abs(float(offset))
                timeout, fail   = check_status(when, poll)

    except OSError:
        pass

    create_record('sys.ntp.fail',    fail)
    create_record('sys.ntp.timeout', timeout)
    create_record('sys.ntp.offset',  offset)


# 判断上次同步状态, return (timeout, fail)
def check_status(when, poll):

    timeout, fail = 0, 1
    try:
        if int(poll) - int(when) >= 0:
            timeout, fail = 0, 0
        else:
            timeout, fail = 1, 0
    except:
        pass

    return timeout, fail

def create_record(metric, value):
    record = {}
    record['metric']      = metric
    record['endpoint']    = endpoint
    record['timestamp']   = int(time.time())
    record['step']        = 600
    record['value']       = value
    record['counterType'] = 'GAUGE'
    record['tags']        = ''
    data.append(record)

if __name__ == '__main__':

    retry = 3
    retry_interval = 3
    status = 1
    for i in range(0, retry):
        data = []
        fetch_ntp_state()

        if data[0]['value'] == 0 and data[1]['value'] == 0 or retry == i+1:
            break
        time.sleep(retry_interval)
    data.append({"endpoint": endpoint, "metric": "monitor.scripts.health", "timestamp": int(time.time()), "step": 600, "value": status, "counterType": "GAUGE", "tags": "scripts=600_ntp.py"})
    print json.dumps(data)
