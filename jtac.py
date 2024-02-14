import sys, os
from datetime import datetime
import getpass
import readline

from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell


DATE = datetime.now().strftime("%d_%m_%Y")
TIME = datetime.now().strftime("%H_%M")
pwd = os.popen('pwd').read()
pwd = str(pwd).replace("\n", "")

def scp_download(dev, rpath, lpath):
    from jnpr.junos.utils.scp import SCP
    try:
        with SCP(dev, progress=True) as scp1:
            scp1.get(rpath, local_path=lpath)
    except Exception as err:
        print(err)

print('\n Enter information for affected device: \n')
device_ip = input('DNS hostname or IP address for device: ')
username =  input('Username for device: ')
password = getpass.getpass()
print('\n Enter information for JTAC Portal: \n')
Case_ID = input('JTAC Case ID: ')
jtac_server_ip = input('JTAC Server IP address or DNS for SFTP: ')
jtac_username =  input('Username for JTAC SFTP: ')
jtac_password = getpass.getpass()

output_folder = ('mkdir ' + str(pwd) + '/' + str(Case_ID) + '_' + str(DATE) + '_' + str(TIME))
os.system(output_folder)

RSI = ('cli -c "request support information | save /var/tmp/' + str(device_ip) + '_' + str(DATE) + '_' + str(TIME) + '_RSI"')
print('\n Taking RSI of ' + str(device_ip) + ' Locally \n')
dev = Device(host=device_ip, user=username, passwd=password)
shell = StartShell(dev)
shell.open()
shell.run(RSI)
shell.close

rpath= ('/var/tmp/' + str(device_ip) + '_' + str(DATE) + '_' + str(TIME) + '_RSI')
lpath= (str(pwd) + '/' + str(Case_ID) + '_' + str(DATE) + '_' + str(TIME) + '/')

print('\n Downloading RSI of ' + str(device_ip) + ' To ' + str(lpath) + "\n")
scp_download(dev, rpath, lpath)

print('\n Uploading RSI of ' +  str(device_ip) + ' To ' + str(jtac_server_ip) + "\n")
upload = ("echo put " + str(lpath) + str(device_ip) + '_' + str(DATE) + '_' + str(TIME) + '_RSI | sshpass -p ' + str(jtac_password) + ' sftp ' + str(jtac_username) + '@' + str(jtac_server_ip))

os.system(upload)




