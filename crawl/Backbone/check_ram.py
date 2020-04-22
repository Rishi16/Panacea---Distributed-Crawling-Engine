import threading
from queue import Queue
import time
import essential
from random import randint
import datetime
import os
import wmi
from socket import *
import pythoncom
from shutil import copy2
import pandas as pd
from hurry.filesize import size

current_path = os.path.dirname(os.path.abspath(__file__))
server_details_path = current_path + '/servers.txt'
server_details = essential.file_to_list(server_details_path)
for each_server in server_details:
    server_con_details = each_server.split('\t')
    server_name = server_con_details[0]
    server_ip = server_con_details[1]
    server_username = server_con_details[2]
    server_password = server_con_details[3]
    print('Starting server - ', str(server_name))
    connection = ''
    try:
        print("Establishing connection to " + str(server_ip))
        connection = wmi.WMI(server_ip, user=server_username, password=server_password)
        print("Connection established")
    except wmi.x_wmi:
        print("Your Username and Password of " + getfqdn(server_ip) + " are wrong.")
        sys.exit()

    # process_id, result = connection.Win32_Process.Create(
    #     CommandLine='cmd.exe /c taskkill /im chrome.exe /f',
    #     CurrentDirectory='c:\\')
    # process_id, result = connection.Win32_Process.Create(
    #     CommandLine='cmd.exe /c taskkill /im chromedriver.exe /f',
    #     CurrentDirectory='c:\\')

    try:
        perf = connection.Win32_PerfFormattedData_PerfOS_System()
        # itime, btime, ltime = os.InstallDate, os.LastBootUpTime, os.LocalDateTime
        uptime = perf[-1].SystemUpTime
        print('Uptime for ' + str(server_name) + ' is - ', datetime.timedelta(seconds=int(uptime)))
        # for i in connection.Win32_ComputerSystem():
        #     print(size(int(i.TotalPhysicalMemory)), "bytes of physical memory")
        #
        # for os in connection.Win32_OperatingSystem():
        #     print(size(int(os.FreePhysicalMemory)), "bytes of available memory")
    except Exception as e:
        print(e)