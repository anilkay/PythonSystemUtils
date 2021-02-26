"""
Find ADB opened devices Throught the Network.
İf you want to find all possible debug devices in your company you can
use this script.
Usage:
python adbdiscover.py ip/subnet
python adbdiscover.py 192.168.11.0/24
or
chmod +x adbdiscover.py
./adbdiscover.py ip/subnet
"""
import sys
import os
import subprocess
from multiprocessing import Pool,Manager
import ipaddress

NUMBER_OF_PROCESSES=8
GENERIC_ARGUMENT_ERROR="Argument should be ip/subnet ex: 192.168.7.0/24"
ARGUMENT_LEN=len(sys.argv)

if ARGUMENT_LEN<2 or ARGUMENT_LEN>=3:
    print(GENERIC_ARGUMENT_ERROR)
    sys.exit(1)

def have_connectable_android_devices(arguments,port=5555):
    founded_ips=arguments[0]
    ip=arguments[1]
    print("İp of: ",ip)
    try:
        output=subprocess.check_output(["adb","connect",ip+":"+str(port)])
        output=output.decode('utf-8')
        print(output)
        if output.startswith("connect"):
            founded_ips.append(ip)
            print("Possible Device:",ip)
            subprocess.call("adb","disconnect")
    except Exception as e:
        pass#print(e) 
    return 1

possible_ips=[]
try:
    possible_ips=[str(ip) for ip in ipaddress.IPv4Network(sys.argv[1])]
except:
    print(GENERIC_ARGUMENT_ERROR)
    sys.exit(1)
p=Pool(NUMBER_OF_PROCESSES)

with Manager() as manager:
    founded_ips=manager.list()
    processes=[]
    list_ips=[]
    for ip in possible_ips:
        list_ips.append([founded_ips,ip])

    p.map(have_connectable_android_devices,list_ips)
    os.system("clear")
    print("Finished all things.")
    print("Founded IPS: ")
    print(founded_ips)
subprocess.run(["adb","disconnect"])
