from win32con import SW_SHOWNORMAL
import general
import wmi
from socket import *
import time
import os



def check_size():
    print('Checking size')

current_path = os.path.dirname(os.path.abspath(__file__))
properties_file = current_path + '\\properties.config'
property, server_count = general.read_properties(properties_file)

connection = ''
ip = "192.168.118.62"
username = "indiaeclerx\harsh.dubey"
password = "zxcvzxcv@123"
ip = str(property['ip'])
username = str(property['username'])
password = str(property['password'])
try:
    print ("Establishing connection to " + str(ip))
    connection = wmi.WMI(ip, user=username, password=password)
    print("Connection established")
except wmi.x_wmi:
    print("Your Username and Password of " + getfqdn(ip) + " are wrong.")

try:
    process_id, result = connection.Win32_Process.Create(
        CommandLine='cmd.exe /c get_input.exe', CurrentDirectory='D:\\harsh_shared\\final_files\\Harsh\\test2')
    # process_id, result = connection.Win32_Process.Create(CommandLine='cmd.exe /c mkdir D:\\temp')
    # watcher = connection.watch_for(
    #     notification_type="Deletion",
    #     wmi_class="Win32_Process",
    #     delay_secs=1,
    #     ProcessId=process_id
    # )
    # watcher()
    # for process in connection.Win32_Process():
    #     print(process.ProcessId, process.Name)
    print(process_id)
    while(True):
        process_found = False
        all_process = connection.Win32_Process(ProcessId=process_id)
        for process in all_process:
            print(process.ProcessId, process.Name)
            if process_id == process.ProcessId:
                process_found = True
                check_size()
                time.sleep(1)
                break
        if process_found == False:
            break
except Exception as e:
    print(e)

print('done')
