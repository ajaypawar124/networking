import paramiko
import getpass
from paramiko import client, ssh_exception
from tabulate import tabulate
import readline
import time
import csv
from datetime import datetime
import sys, os
from termcolor import colored

def get_confirmation(message):
    from termcolor import colored
    message = (str(message) +  " (y or n) : ")
    chose = ""
    while chose != 'n':
        chose = input(str(message))
        if chose == 'y':
            return chose
        elif chose == 'n':
            print('\nSkipping...\n')
            break
        else:
            print(colored('\nPlease enter choice from menu (y or n):', 'red'))

def sleep(seconds):
    import datetime
    import time
    total_seconds = int(seconds)
    while total_seconds > 0:
        timer = datetime.timedelta(seconds = total_seconds)
        print("Remaining time: ", timer, end="\r")
        time.sleep(1)
        total_seconds -= 1

def get_data_from_output(path, output, group=1, type='regex'):
    if type == "regex":
        import re
        output = str(output).replace("n'", " ")
        output = str(output).replace("\ ", " ")
        data = re.search(path, output)
        group = int(group)
        try:
            data = data.group(group)
            return data
        except:
            return 'NA'
    elif type == "xml":
        print('Not yet Supported')
        return 'XML NA'
    else:
        print('invalid data format')

def check_device_vendor(ssh_client):
    stdin, stdout, stderr = ssh_client.exec_command('show version \n')
    output = stdout.readlines()
    if 'JUNOS' in str(output):
        return "Juniper"
    elif 'Cisco' in str(output):
        return "Cisco"
    else:
        return "Unsupported"

def connect_to_device(credintials_list):
    import paramiko
    from paramiko import client, ssh_exception
    from termcolor import colored
    Attempt = 1
    for cred in credintials_list:
        username = cred[0]
        password = cred[1]
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(device, port=22, username=username, password=password, look_for_keys=False, allow_agent=False)
            print(colored("Attempt: " + str(Attempt) + " Connection to " + str(device) + " is succesfull", 'green'))
            return ssh_client
            if ssh_client:
                break
        except ssh_exception.NoValidConnectionsError:
            print(colored("SSH Port not reachable on " + str(device), 'red'))
            break
        except ssh_exception.AuthenticationException:
            print(colored("Attempt: " + str(Attempt) + " Authentication failed, check credentials for " + str(device), 'red'))
        except ssh_exception.socket.error:
            print(colored("Connection time out for " + str(device), 'red'))
            break
        Attempt = Attempt + 1

def get_credentials():
    import getpass
    import readline
    user = input("\nUsername for devices: ")
    passw = getpass.getpass()
    code = ""
    credintials_list = [[user, passw]]
    while code != "n":
        code = input("\nDo you want to add another username ( y or n): ")
        if code == "y":
            user = input("Username for devices: ")
            passw = getpass.getpass()
            credintials_list.append([user, passw])
        elif code == "n":
            print("\nThank you for providing data\n")
        else:
            print("\n Please provide input as y or n: ")
    return credintials_list

data = [
        ["Device IP", "Hostname", "Vendor", "Model", "Version", "Uptime"]
        ]

credintials_list = get_credentials()

with open('hosts.txt','r') as f:
    ip = f.read().splitlines()
for device in ip:
    ssh_client = connect_to_device(credintials_list)
    if ssh_client:
        vendor = check_device_vendor(ssh_client)
        if str(vendor) == "Juniper":
            stdin, stdout, stderr = ssh_client.exec_command('show version \n')
            output = stdout.readlines()
            stdin, stdout, stderr = ssh_client.exec_command('show system uptime \n')
            uptime = stdout.readlines()
            ssh_client.close()

            model = get_data_from_output(path='Model:\s(\w+)', output=output)
            version = get_data_from_output(path='Junos:\s(\S+)', output=output)
            hostname = get_data_from_output(path='Hostname:\s(\S+)', output=output)
            uptime = get_data_from_output(path='System\s+booted:\s+(\S+\s+\S+\s+\S+\s+)(\S+\s+\S+\s+\S+)', output=uptime)
            data.append(
                [device, hostname, vendor, model, version, uptime]
            )

        elif str(vendor) == "Cisco":
            ssh_client = connect_to_device(credintials_list)
            stdin, stdout, stderr = ssh_client.exec_command('show version \n')
            output = stdout.readlines()
            ssh_client.close()

            model = get_data_from_output(path='Cisco\s+IOS\s+Software,\s+(\S+)', output=output)
            version = get_data_from_output(path='Version\s+(\S+)', output=output)
            hostname = get_data_from_output(path='(\S+)\s+uptime\s+is', output=output)
            uptime = get_data_from_output(path='uptime\s+is\s+(\S+\s+\S+)', output=output)
            data.append(
                    [device, hostname, vendor, model, version, uptime]
                    )

        else:
            print("Device type is not supported")
            ssh_client.close()
            data.append(
                    [device, 'Unsupported', 'Unsupported', 'Unsupported', 'Unsupported', 'Unsupported']
                    )

    else:
        data.append(
            [device, 'Fail', 'Fail', 'Fail', 'Fail', 'Fail']
        )


foroutput = tabulate(data, tablefmt="fancy_grid", showindex="always", missingval='NA')
print(colored('****************', 'yellow'))
print(colored('   DATA TABLE              ', 'yellow'))
print(colored('****************', 'yellow'))
print(colored(foroutput, 'yellow'))

outputfile = get_confirmation('Do you need output in csv file')
if outputfile == "y":
    DATE = datetime.now().strftime("%d_%m_%y")
    TIME = datetime.now().strftime("%H_%M")
    filename = ( "device_data_" + str(DATE) + "_" + str(TIME) + ".csv" )
    pwd = os.popen('pwd').read()
    pwd = str(pwd).replace("\n", "")
    print('Generating data file:')
    #halt(5)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for data in data:
            row_list = data
            writer.writerow(row_list)
    print('\ncsv file with data: ' + str(pwd) + "/" + str(filename))




        