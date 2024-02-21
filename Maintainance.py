#You Need to create two text files one as pre_post_commands.txt and one compare_commands.txt in same location where this script will be placed
#Try to put commands in compare_commands.txt which will not have time, as it will change and show the differed text in compare results.

import os
from datetime import datetime
import readline
import argparse
DATE = datetime.now().strftime("%d_%m_%Y")
TIME = datetime.now().strftime("%H_%M")



def get_compare_results(file1, file2):
    import difflib
    with open(file1) as file_1:
        file_1_text = file_1.readlines()
    with open(file2) as file_2:
        file_2_text = file_2.readlines()
    lines = ''
    for line in difflib.unified_diff(
            file_1_text, file_2_text, fromfile='file1.txt',
            tofile='file2.txt', lineterm=''):
            lines = ( str(lines) + '\n' + str(line))
            print(line)
    return lines

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


def get_current_directory_unix():
    pwd = os.popen('pwd').read()
    pwd = str(pwd).replace("\n", "")
    pwd = (str(pwd) + "/")
    return pwd

def sleep(seconds):
    import datetime
    import time
    total_seconds = int(seconds)
    while total_seconds > 0:
        timer = datetime.timedelta(seconds = total_seconds)
        print("Remaining time: ", timer, end="\r")
        time.sleep(1)
        total_seconds -= 1

def get_integer(message):
    import readline
    from termcolor import colored
    while True:
        try:
            chose = int(input(str(message)))
            return chose
        except ValueError:
            print(colored("The input is not an integer.", 'red'))
            continue

def get_device_handle(credintials_list, device_ip, device_type):
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
            print(colored("Attempt: " + str(Attempt) + " Connection to " + str(device_ip) + " is succesfull", 'green'))
            if device_handle:
                return device_handle
                break
        except AuthenticationException:
            print(colored("Attempt: " + str(Attempt) + " Authentication failed, check credentials for " + str(device_ip), 'red'))
        except NetMikoTimeoutException:
            print(colored("Connection time out for : " + str(device_ip), 'red'))
            break
        except SSHException:
            print(colored("SSH Port not reachable on : " + str(device_ip), 'red'))
            break
        Attempt = Attempt +1



def get_confirmation(message):
    from termcolor import colored
    import readline
    message = (str(message) +  " (y or n) : ")
    chose = ""
    while chose != 'n':
        chose = input(str(message))
        if chose == 'y':
            return chose
        elif chose == 'n':
            print('\nSkipping...\n')
            return chose
            break
        else:
            print(colored('\nPlease enter choice from menu (y or n):', 'red'))
def get_input(var_name, message):
    if auto_input := getattr(cli_args, var_name, None):
        return auto_input
    else:
        return input(message)

parser = argparse.ArgumentParser()
parser.add_argument('--host', default=None, required=False)
cli_args = parser.parse_args()

credintials_list = get_credentials()
device_ip = get_input("host", "Enter Device hostname or IP Address: ")
device_handle = get_device_handle(credintials_list, device_ip, 'juniper')

with open('pre_post_commands.txt','r') as f:
    commands = f.read().splitlines()
with open('compare_commands.txt','r') as f:
    ccommands = f.read().splitlines()
name = (str(device_ip) + '_' + str(DATE) + '_' + str(TIME))

if device_handle:
    os.system("mkdir " + str(name))
    pre_checks_file = (str(name) + '/' + str(name) + '_pre_checks.log')
    with open(pre_checks_file, "w") as logfile:
        print('\n Starting Pre Checks for : ' + str(device_ip) + '\n')
        for command in commands:
            print(("============================================================="), file=logfile)
            print('Pre Checks: ' + str(command) + ' : ', file=logfile)
            print(("=============================================================\n"), file=logfile)
            output = device_handle.send_command(str(command), read_timeout=120)
            print(output, file=logfile)
    compare_file1 = (str(name) + '/' + 'compare_file1.log')
    with open(compare_file1, "w") as logfile:
        for ccommand in ccommands:
            print(("============================================================="), file=logfile)
            print('Pre Checks: ' + str(ccommand) + ' : ', file=logfile)
            print(("=============================================================\n"), file=logfile)
            output = device_handle.send_command(str(ccommand), read_timeout=120)
            print(output, file=logfile)
        print('\n Finished Pre Checks for : ' + str(device_ip) + '\n')
    script_trigger = get_confirmation('\nDo you want script to trigger (y) or trigger will be done manually (n) : ')
    if script_trigger == 'y':
        n = get_integer('\nHow many commands are needed for this trigger: ')
        n = n + 1
        tcommands1 = ''
        for i in range(1, n):
            tcommand1 = input('\n Command ' + str(i) + ": ")
            tcommands1 = (str(tcommands1) + '\n' + str(tcommand1))
        trigger_file = (str(name) + '/' + 'trigger.txt')
        with open(trigger_file, "w") as file:
            file.write(tcommands1)
        with open(trigger_file, "r") as file:
            tcommands = file.read().splitlines()
        with open(trigger_file, "w") as logfile:
            print('\n Starting Executing Trigger on : ' + str(device_ip) + '\n')
            for tcommand in tcommands:
                print(("============================================================="), file=logfile)
                print('Trigger: ' + str(tcommand) + ' : ', file=logfile)
                print(("=============================================================\n"), file=logfile)
                output = device_handle.send_command(str(tcommand), read_timeout=120)
                print(output)
                print(output, file=logfile)
        print('\n Finished Executing Trigger on : ' + str(device_ip) + '\n')
        slp = get_integer('Enter time needed for device recovery: ')
        sleep(slp)
        confirmation = ''
        while confirmation != 'y':
            confirmation = get_confirmation('\nHit y to proceed with post_checks or n to wait:')
            if confirmation == 'n':
                slp = get_integer('Enter time needed for device recovery: ')
                sleep(slp)
        post_checks_file = (str(name) + '/' + str(name) + '_post_checks.log')
        with open(post_checks_file, "w") as logfile:
            print('\n Starting Post Checks for : ' + str(device_ip) + '\n')
            for command in commands:
                print(("============================================================="), file=logfile)
                print('Post Checks: ' + str(command) + ' : ', file=logfile)
                print(("=============================================================\n"), file=logfile)
                output = device_handle.send_command(str(command), read_timeout=120)
                print(output, file=logfile)
            print('\n Finished Post Checks for : ' + str(device_ip) + '\n')
    elif script_trigger == 'n':
        slp = get_integer('Enter time needed for Trigger and device recovery: ')
        sleep(slp)
        confirmation = ''
        while confirmation != 'y':
            confirmation = get_confirmation('\nHit y to proceed with post_checks or n to wait:')
            if confirmation == 'n':
                slp = get_integer('Enter time needed for device recovery: ')
                sleep(slp)
        post_checks_file = (str(name) + '/' + str(name) + '_post_checks.log')
        with open(post_checks_file, "w") as logfile:
            print('\n Starting Post Checks for : ' + str(device_ip) + '\n')
            for command in commands:
                print(("============================================================="), file=logfile)
                print('Post Checks: ' + str(command) + ' : ', file=logfile)
                print(("=============================================================\n"), file=logfile)
                output = device_handle.send_command(str(command), read_timeout=120)
                print(output, file=logfile)
        compare_file2 = (str(name) + '/' + 'compare_file2.log')
        with open(compare_file2, "w") as logfile:
            for ccommand in ccommands:
                print(("============================================================="), file=logfile)
                print('Post Checks: ' + str(ccommand) + ' : ', file=logfile)
                print(("=============================================================\n"), file=logfile)
                output = device_handle.send_command(str(ccommand), read_timeout=120)
                print(output, file=logfile)
            print('\n Finished Post Checks for : ' + str(device_ip) + '\n')
    device_handle.disconnect()
    results = get_compare_results(compare_file1, compare_file2)
    results_file = (str(name) + '/' + str(name) +'_results.log')
    with open(results_file, "w") as logfile:
        print(results, file=logfile)
    print('\n\nFinished Executing Script\n\n')

