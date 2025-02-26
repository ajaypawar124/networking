import os
from datetime import datetime
import readline
import argparse
import csv
import os
import datetime
from time import time
from termcolor import colored


def get_credentials():
    user = 'user'   #or input('Enter username:, )
    passw = 'password'  #or getpass
    credintials_list = [[user, passw]]
#            credintials_list.append([user, passw])
    return credintials_list

def get_device_handle(credintials_list, device_ip, device_type, hostname):
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetMikoTimeoutException , AuthenticationException, SSHException
    from termcolor import colored
    Attempt = 1
    for cred in credintials_list:
        username = cred[0]
        password = cred[1]
        router_data = {
            'device_type': device_type,
            'host': device_ip,
            'username': username,
            'password': password,
            'port': 22,
        }
        try:
            device_handle = ConnectHandler(**router_data)
            print(colored("Attempt: " + str(Attempt) + " Connection to " + str(hostname) + " is succesfull", 'green'))
            if device_handle:
                return device_handle
                break
        except AuthenticationException:
            print(colored("Attempt: " + str(Attempt) + " Authentication failed, check credentials for " + str(hostname), 'red'))
        except NetMikoTimeoutException:
            print(colored("Connection time out for : " + str(hostname), 'red'))
            break
        except SSHException:
            print(colored("SSH Port not reachable on : " + str(hostname), 'red'))
            break
        Attempt = Attempt +1

credintials_list = get_credentials()

ctime=datetime.datetime.now().strftime('%d-%m-%y_%H_%M')
cdir=os.getcwd()
folder_name= (str(cdir) + "/BACKUPs/CCL_BACKUP_" + str(ctime))
cfolder=("mkdir " + str(folder_name))
print (str(cfolder))
os.system(str(cfolder))

with open('devices.txt') as inf:
    reader = csv.reader(inf, delimiter=" ")
    ip_addresses = list(zip(*reader))[0]
with open('devices.txt') as inf:
    reader = csv.reader(inf, delimiter=" ")
    hostnames = list(zip(*reader))[1]

for ipaddress, hostname in zip(ip_addresses,hostnames):
    spath=(str(folder_name) + "/" + str(hostname) + ".txt")
    try:
        print("\nTaking Backup of " + str(hostname))
        device_handle = get_device_handle(credintials_list, ipaddress, 'juniper', hostname)
        backup=open(spath, "w")
        backup.write(device_handle.send_command('show configuration | no-more', read_timeout=120))
        backup.close
        print(colored("Config Backup Successful for " + str(hostname), 'yellow'))
    except:
        print(colored("\nUnable to Connect to " + str(hostname) + " On " + str(ipaddress), 'red'))
