#!/usr/bin/env python3
"""
System Health Inform to SLACK CHANNEL VİA SLACK WEBHOOKS
Example Usage:python3 healthchecks.py network_interface |python3 healthchecks.py en0
cpu,disk,memory and network utilization check   
"""
import psutil
import requests
import time
import sys
import json

ROOT="/"
MAX_CPU_PERCENT=80
MAX_DISK_PERCENT=89
MAX_MEMORY_PERCENT=90
MAX_NETWORK_MEGABIT=99
NETWORK_INTERFACE_ARGUMENT_ERROR_MESSAGE="You should write intended Network Interface"
def define_net_interface():
    if len(sys.argv)>=2:
       return sys.argv[1]
    else :
       if psutil.LINUX:
          return "eth0"
       elif psutil.MACOS:
          return "en0"
       else:
          print(NETWORK_INTERFACE_ARGUMENT_ERROR_MESSAGE)
          sys.exit(14)

NET_INTERFACE=define_net_interface()       
BYTES_TO_MEGABITS_DENOMINATOR=1024*1024
CPU_MESSAGE_FORMAT="CPU USAGE IS MORE THAN MAX: {}"
DISK_MESSAGE_FORMAT="DISK USAGE IS MORE THAN MAX: {} "
MEMORY_MESSAGE_FORMAT="MEMORY USAGE İS MORE THAN MAX: {}"
NETWORK_MESSAGE_FORMAT="TOO MUCH NETWORK USAGE: {}"

def get_slack_url():
    with open('config.json') as json_file:
         config_json=json.load(json_file)
    slack_url=config_json["slack_webhook_url"]
    return slack_url

SLACK_WEBHOOKS=get_slack_url()
def notify_to_slack(error_message="Undefined"):
    response = requests.post(SLACK_WEBHOOKS, json = {'text':error_message})
    status_code=response.status_code
    if status_code>199 and status_code<300:
        pass
    else:
        print("Problem in Sending Requests") #TODO write as log    


def percent_of_cpu():
    return psutil.cpu_percent(1)

def percent_of_disk():
    disk_usage=psutil.disk_usage(ROOT)
    return disk_usage.percent

def percent_of_memory():
    virtual_memory=psutil.virtual_memory()
    return virtual_memory.percent

def network_megabits_second(net_interface="eth0"):
    net_in_ps_start = psutil.net_io_counters(pernic=True, nowrap=True)[net_interface]
    megabits_start=net_in_ps_start.bytes_recv/BYTES_TO_MEGABITS_DENOMINATOR
    time.sleep(1)
    net_in_ps_finish = psutil.net_io_counters(pernic=True, nowrap=True)[net_interface]
    megabits_end=net_in_ps_finish.bytes_recv/BYTES_TO_MEGABITS_DENOMINATOR
    megabits=megabits_end-megabits_start
    return megabits

def network_get_megabit(net_interface="eth0"):
    megabits=0
    for i in range(1,10):
        megabits=network_megabits_second(net_interface)
        if megabits>0:
            break   
    return megabits

cpu_percent=percent_of_cpu()
disk_percent=percent_of_disk()
memory_percent=percent_of_memory()
network_megabit=network_get_megabit(NET_INTERFACE)

if cpu_percent>MAX_CPU_PERCENT:
    notify_to_slack(CPU_MESSAGE_FORMAT.format(cpu_percent))

if disk_percent>MAX_DISK_PERCENT:
    notify_to_slack(DISK_MESSAGE_FORMAT.format(disk_percent))

if memory_percent>MAX_MEMORY_PERCENT:
    notify_to_slack(MEMORY_MESSAGE_FORMAT.format(memory_percent))
    
if network_megabit>MAX_NETWORK_MEGABIT:
    notify_to_slack(NETWORK_MESSAGE_FORMAT.format(network_megabit))   
