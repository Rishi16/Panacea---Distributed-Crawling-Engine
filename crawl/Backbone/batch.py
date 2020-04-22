"""
Author: Harsh Dubey
Windows Remote Connection Library: WMI

(Please feel free to use this code for personal use only without changing it or its functionality)
"""

import threading
import time
from crawl.Backbone import essential
import datetime
from crawl.Backbone import wmi
from socket import *
import pythoncom
from shutil import copy2
import pandas as pd
import general
from crawl.Backbone import status
from crawl.Backbone.log_writer import log_Writer
import crawl.tasks
import os
import re
import logging

class Batch:
    # This function is initiating the batch and creating the threads for each server
    active_servers = 0
    @staticmethod
    def start(batch_id, batch_run_id, batch_data, region, team_name, user_id, input_file_path, script_path, proxies_file_path, server_details, num_of_attempts, time_out, logger, encoding='utf-8'):
        try:
            batch_name = batch_data
            # log_path = os.path.join("E:\\panacea", "team_data", str(team_name), "Batches", str(batch_name), "logs",
            #                         str('batch.log'))
            # print(log_path)
            # logging.basicConfig(filename=log_path,
            #                     filemode='a',
            #                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            #                     datefmt='%H:%M:%S',
            #                     level=logging.DEBUG)
            #
            # logger = logging.getLogger(str(user_id))
            startTime = datetime.datetime.now()
            logger.info("Batch_start_time - "+str(startTime))
            # print(status.batch_status[team_name][batch_name])
            # batch_log_file = status.current_path + '/Team_data/' + str(team_name) + '/Batches/' + str(batch_name) + '/logs/batch_logs.log'
            # batchlog = log_Writer(batch_log_file)
        except Exception as e:
            print(e)
            essential.write_file(str(status.current_path) + '/logs/' + str(team_name) + '.txt', str(e) + ' | ' + str(batch_data) + ' | Exception in start method while creating local folders and batch log object of batch.py' + str(datetime.datetime.now()))
            return

        try:
            print('------------- Starting Batch -------- ' + str(batch_name))
            logger.info("Starting batch")
            # batchlog.write('Starting Batch - ' + str(batch_name) + ' - ' + str(datetime.datetime.now()))  # Writing Batch logs
            # batch_properties_file = status.current_path + '/Team_data/' + str(team_name) + '/Batches/' + str(batch_name) + '/batch_properties.pbf'
            batch_property = {'region': str(region), 'num_of_attempts': num_of_attempts, 'time_out': time_out, 'user_name': 'panacea', 'resume_crawl': 'on', 'encoding': encoding, 'stop':0}
            proxies_path = 'E:/Harsh/django_projects/panacea/media/' + proxies_file_path
            script_path = 'E:/Harsh/django_projects/panacea/media/' + script_path
            # server_details_path = status.current_path + '/Team_data/' + str(team_name) + '/Servers/' + batch_property['servers']
            logger.info("Converting server dettails into list(essential.pipe_to_list)")
            server_details = essential.pipe_to_list(server_details)
            input_file_path = 'E:/Harsh/django_projects/panacea/media/' + input_file_path
            logger.info("distributing inputs(essential.distribute_input)")
            if not essential.get_status(batch_id) == 'resumed':
                essential.update_status(batch_id, "splitting")
            total_inputs, dist_inputs = essential.distribute_input(input_file_path, server_details, batch_id)

            # this thread will monitor the status for crawling on all the servers
            logger.info("Starting thread for status monitor")
            crawl_status_monitor_thread_name = 'crawl_status_monitor'
            t1 = threading.Thread(target=Batch.crawl_status_monitor, name=crawl_status_monitor_thread_name,args=[batch_id, batch_run_id, server_details, batch_name, team_name, logger])
            t1.daemon = True
            t1.start()

            # updating batch status in database
            # status.batch_status = 'running'
            logger.info("Checking resumed/running batch condition")
            if not essential.get_status(batch_id) == 'resumed':
                essential.update_status(batch_id, "distributing")

            input_itr = 0
            server_threads = []
            logger.info("Checking if the script type is vbs")
            if ".vbs" in str(script_path).lower():
                py_script_path = os.path.join(os.path.abspath(os.path.join(script_path, os.pardir)),
                                              str(datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")) + ".vbs")
                logger.info("Running Batch.make_vb_compatible")
                Batch.make_vb_compatible(script_path, py_script_path)
                script_path = py_script_path
            logger.info("Setting up the environment in each server")

            for i, each_server in enumerate(server_details):
                # Setup the environment on each server
                if not essential.get_status(batch_id) == 'resumed':
                    essential.update_status(batch_id, "distributing-"+str(len(server_details)-i))
                logger.info("environment setup-"+str(each_server[0]))
                batch_path = Batch.setup_environment(batch_id, each_server, dist_inputs[input_itr], team_name,
                                                     batch_name, script_path, proxies_path, batch_property,
                                                     num_of_attempts, time_out, logger)
                input_itr += 1
            logger.info("Checking if the batch status is resumed")
            essential.update_status(batch_id, "initiating")
            logger.info("Initiating run_on_server")
            for i, each_server in enumerate(server_details):
                essential.update_status(batch_id, "initiating-"+str(len(server_details)-i))
                server_name = each_server[0]
                logger.info("Initiating process on-"+str(server_name))
                t = threading.Thread(target=Batch.run_on_server, name=server_name, args=[batch_id, batch_run_id, each_server, batch_name, team_name, logger])
                t.daemon = True
                t.start()
                server_threads.append(t)
                Batch.active_servers += 1
            logger.info("batch is running")
            time.sleep(10)
            essential.update_status(batch_id, "running")
            logger.info("Joining")
            for t in server_threads:
                t.join()
            logger.info("Running exclusive Batch.get_update_count")
            Batch.get_update_count(batch_id, server_details, batch_name, team_name, logger)
            ins_backup_paths = Batch.clean_batch_process(batch_id, server_details, team_name, batch_name)
            # Batch.generate_report(ins_backup_paths, team_name, batch_name, batch_id)
            # updating batch status in database
            # status.batch_status = 'completed'
            print('batch - ' + str(batch_name) + ' for Team - ' + str(team_name) + ' has Completed')
            logger.info("batch completed")
            # batchlog.write('Batch Completed' + ' - ' + str(batch_name) + ' - ' + str(datetime.datetime.now()))  # Writing Batch logs
            batch_state = essential.get_status(batch_id)
            essential.update_status(batch_id, "generating report")
            try:
                logger.info("Generationg Report for " + batch_name)
                print("Generationg Report for " + batch_name)
                crawl.tasks.generate_batch_report("", team_name, batch_name, batch_id, batch_run_id)
            except Exception as e:
                logger.error('Report Generation Failed:' + str(e))
                print('Report Generation Failed:' + str(e))
            essential.update_status(batch_id, "analysing proxies")
            try:
                logger.info("Generationg Proxy Analysis for " + batch_name)
                print("Generationg Proxy Analysis for " + batch_name)
                Batch.get_proxy_analysis(batch_id, server_details, batch_name, team_name, logger)
                logger.info("Done!")
            except:
                logger.error('Proxy Analysis Failed:' + str(e))
                print('Proxy Analysis Failed:' + str(e))
            if batch_state == 'paused':
                essential.update_status(batch_id, 'paused')
            if batch_state == 'forced':
                essential.update_status(batch_id, 'forced')
            if not essential.get_status(batch_id) in ['paused', 'stopped', 'forced']:
                essential.update_status(batch_id, 'completed')
        except Exception as e:
            print(e)
            logger.error(e)
            # batchlog.write(str(e) + ' | ' + str(batch_name) + ' | Exception in starting of batch in batch.py | ' + str(datetime.datetime.now()))  # Writing Batch logs
            # updating batch status in database
            # status.batch_status = 'exception'
            logger.error("Running essential.update_status")
            essential.update_status(batch_id, "exception")
            # status.batch_in_system[team_name].remove(batch_data)
            return

    # This function will monitor the status of crawling for every batch
    @staticmethod
    def crawl_status_monitor(batch_id, batch_run_id, server_details, batch_name, team_name, logger):
        while (True):
            try:
                time.sleep(10)
                # logger.info("Running Batch.get_update_count")
                Batch.get_update_count(batch_id, server_details, batch_name, team_name, logger)
                # logger.info("Checking batch status paused/completed/exception")
                if essential.get_status(batch_id) in ['paused', 'completed', 'exception', 'forced']:
                    logger.info("Completed. Exiting Monitor")
                    break

            except Exception as e:
                # print(e)
                logger.error(e)
                # batchlog.write(
                #     str(e) + ' | ' + str(batch_name) + ' | Exception in crawl_status_monitor of batch.py | ' + str(datetime.datetime.now()))  # Writing Batch logs
    @staticmethod
    def get_proxy_analysis(batch_id, server_details, batch_name, team_name, logger):
        try:
            logger.info("Running Batch.get_proxy_analysis")
            print("Running Batch.get_proxy_analysis")
            df = pd.DataFrame()
            summary = pd.DataFrame()
            cols = ['timestamp', 'attempt', 'url', 'response_url', 'status_code', 'proxy']
            for server in server_details:
                try:
                    df = df.append(pd.read_csv(
                        '\\\\' + str(server[0]) + '\\e$\\Panacea\\Team_data\\' + str(
                        team_name) + '\\' + str(batch_name) + '\\request.log',
                        names=cols, header=None, sep='\t'), sort=False, ignore_index=True)
                except Exception as e:
                    logger.error(e)
            df = df.fillna('')
            df = df[~df.status_code.str.match('^http')]
            df = df[~(df.status_code == "")]
            df.loc[df.status_code.str.contains('Max retries exceeded', case=False), 'status_code'] = 'failed'
            df.loc[df.status_code.str.contains('timed out', case=False), 'status_code'] = 'failed'
            df.loc[df.status_code.str.contains('operation did not', case=False), 'status_code'] = 'failed'
            df.loc[df.status_code.str.contains('redirects'), 'status_code'] = 'failed'
            df3 = pd.crosstab(index=[df['proxy']], columns=df['status_code'])

            df3['failed'] = df3.failed
            df3['failurerate'] = df3.failed / (df3.failed + df3['200']) * 100
            df3['failurerate'] = df3['failurerate'].round(2)
            df3['total'] = df3['200'] + df3['failed']
            df3.sort_values('failurerate', ascending=False, inplace=True)
            df3[['total', '200', 'failed', 'failurerate']].to_csv(r'E:\\Panacea\\team_data\\' + str(
                    team_name) + '\\Batches'+ '\\' + str(batch_name)+'\\proxy_analysis.txt', sep='\t', header=False)
            print('Analyzed')
        except Exception as e:
            # print(e)
            logger.error(e)

    @staticmethod
    def get_update_count(batch_id, server_details, batch_name, team_name, logger):
        found = 0
        pnf = 0
        tag_failed = 0
        proxy_blocked = 0
        other = 0
        for each_server in server_details:
            # logger.info("Updating count for-"+str(each_server[0]))
            server_con_details = each_server
            server_name = server_con_details[0]
            server_crawling_status_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
                team_name) + '\\' + str(batch_name) + '\\crawling_status.pbf'
            if os.path.exists(server_crawling_status_file):
                status_values = []
                while (len(status_values) < 5):
                    time.sleep(2)
                    status_values = essential.file_to_list(server_crawling_status_file)
                found += int(status_values[0])
                pnf += int(status_values[1])
                tag_failed += int(status_values[2])
                proxy_blocked += int(status_values[3])
                other += int(status_values[4])
                # logger.info(str(batch_name)+"-"+str(server_name)+"-"+str(status_values[0])+"-"+str(status_values[1])+"-"+str(status_values[2])+"-"+str(status_values[3])+"-"+str(status_values[4]))
                # print(batch_name, server_name, status_values[0], status_values[1], status_values[2],
                #       status_values[3], status_values[4])
        # logger.info("------------------------------------")
        # logger.info(str(essential.get_status(batch_id)))
        # logger.info("Total"+"-"+str(found)+"-"+str(pnf)+"-"+str(tag_failed)+"-"+str(proxy_blocked)+"-"+str(other))
        # logger.info("------------------------------------")
        # print('--------------------------------------')
        # print(essential.get_status(batch_id))
        # print('Total', found, pnf, tag_failed, proxy_blocked, other)
        # print('--------------------------------------')

        # batch_status_file_path_on_tool = status.current_path + '\\Team_data\\' + str(
        #     team_name) + '\\Batches\\' + str(batch_name) + '\\crawling_status.pbf'
        # essential.over_write_file(batch_status_file_path_on_tool, str(found) + '\r\n' + str(pnf) + '\r\n' + str(
        #     tag_failed) + '\r\n' + str(proxy_blocked) + '\r\n' + str(other))
        logger.info("Calling essential.update_batch_completion")
        essential.update_batch_completion(batch_id, found, pnf, tag_failed, proxy_blocked, other)


    @staticmethod
    def make_vb_compatible(vb_file_path, vb_out_file_path, encoding="ANSI"):
        vb_script = essential.read_file(vb_file_path, encoding=encoding)
        vb_script = vb_script.replace('New HTMLPROCESSORLib.ValuePairCollection', 'New value_pair')
        vb_script = vb_script.replace('New HTMLPROCESSORLib.HtmlParser', 'New value_pair')
        vb_script = re.sub(r'(Item\(".*"\)).Value', r'\1', vb_script)
        vb_script = re.sub(r'(Item\(".*"\)).value', r'\1', vb_script)

        value_pair_class_code = """

    Class value_pair
      Private a(500000)
      Private i
      Private d_

      Private Sub Class_Initialize
          i = 0
          Set d_ = CreateObject("Scripting.Dictionary")
      End Sub

      Public Function GetData
        GetData = a
      End Function

      Public Function ResultCount
       ResultCount = i
      End Function

      Public Function AddResult
    	set a(i) = d_
    	i = i + 1
    	Set d_ = CreateObject("Scripting.Dictionary")
      End Function

      Public Sub Add(Name, Value)
        d_(name) = value
      End Sub

      Public Property Let Item(name, value)
        d_(name) = value
      End Property

      Public Property Get Item(name)
        Item = d_(name)
      End Property

      Public Function Exists(name)
        Exists = d_.Exists(name)
      End Function

      Public Sub Remove(name)
        d_.Remove(name)
      End Sub
    End Class

    """
        script_start_code = """

    Function Initialize_script
      if WScript.Arguments.Count < 2 Then
        WScript.Echo "Error! Please provide the input and file location for the script"
        Wscript.Quit
      End If
      DataIn.Add "Itemnumber", Wscript.Arguments.Item(0)
      output_file_path_ = Wscript.Arguments.Item(1)

      DataOut.Add "manufacturer", ""
      DataOut.Add "description", ""
      DataOut.Add "price", ""
      DataOut.Add "stock", ""
      DataOut.Add "partcode", ""
      For iCt = 0 To 19
          DataOut.Add "field" & CStr(iCt), ""
      Next
    End Function

    Function write_output_file(file_path, d)
        Set fsT = CreateObject("ADODB.Stream")
        fsT.Type = 2
        fsT.Charset = "utf-8"
        fsT.Open

        Set fso = CreateObject("Scripting.FileSystemObject")
        If (fso.FileExists(file_path)) Then
           fsT.LoadFromFile(file_path)
           strData = fsT.ReadText()
        Else
           strData = ""
        End If
		
		dataOut_array = d.GetData
		data_to_write = ""
		For i = 0 to d.ResultCount() - 1
			For Each j In dataOut_array(i).Keys
				data_to_write = data_to_write & cstr(cstr(j) & "!:!:!" & cstr(dataOut_array(i).Item(j)) & "|^|^|")
			Next
			data_to_write = data_to_write & "^!^!^"
		Next
        fsT.WriteText strData & data_to_write
        fsT.SaveToFile file_path, 2
    End Function

    Function Finalize_script
      dataOut.AddResult
      file_path = output_file_path_
      Call write_output_file(file_path, dataOut)
    End Function

    Dim output_file_path_
    Set dataOut = New value_pair
    Set DataIn = New value_pair
    Call Initialize_script
    Call start
    Call login
    Call query
    Call getDetails
    Call Finalize_script

    """

        vb_script = value_pair_class_code + vb_script + script_start_code

        essential.over_write_file(vb_out_file_path, vb_script, encoding=encoding)

    # This function will setup the environment on each server
    @staticmethod
    def setup_environment(batch_id, server, input_list, team_name, batch_name, script_path, proxies_path, batch_property, num_of_attempts, time_out, logger):
        # We will use normal file transfer protocol to transfer the files between the servers
        print('setting up the environment')
        server_con_details = server
        server_name = server_con_details[0]
        num_of_threads_for_this_server = server_con_details[2]

        # Generating the server path of the current batch
        logger.info("Generating the server path of the current batch")
        panacea_path = '\\\\' + str(server_name) + '\\e$\\panacea'
        if not os.path.exists(panacea_path):
            os.makedirs(panacea_path)
        team_data_path = str(panacea_path) + '\\Team_data'
        if not os.path.exists(team_data_path):
            os.makedirs(team_data_path)
        team_path = os.path.join(team_data_path, str(team_name))
        if not os.path.exists(team_path):
            os.makedirs(team_path)
        batch_path = os.path.join(team_path, str(batch_name))
        if not os.path.exists(batch_path):
            os.makedirs(batch_path)

        # Writing new inputs and removing old files
        logger.info("Writing new inputs and removing old files")
        if not essential.get_status(batch_id) == 'resumed':
            print("Inside non resumed")
            if os.path.exists(os.path.join(batch_path, 'input_file.txt')):
                os.remove(os.path.join(batch_path, 'input_file.txt'))
            if os.path.exists(os.path.join(batch_path, 'crawling_status.pbf')):
                os.remove(os.path.join(batch_path, 'crawling_status.pbf'))
            if os.path.exists(os.path.join(batch_path, 'final_data.txt')):
                os.remove(os.path.join(batch_path, 'final_data.txt'))
            if os.path.exists(os.path.join(batch_path, 'input_crawled.txt')):
                os.remove(os.path.join(batch_path, 'input_crawled.txt'))
            if os.path.exists(os.path.join(batch_path, 'pnf.txt')):
                os.remove(os.path.join(batch_path, 'pnf.txt'))
            if os.path.exists(os.path.join(batch_path, 'proxy_blocked.txt')):
                os.remove(os.path.join(batch_path, 'proxy_blocked.txt'))
            if os.path.exists(os.path.join(batch_path, 'tag_failed.txt')):
                os.remove(os.path.join(batch_path, 'tag_failed.txt'))
            if os.path.exists(os.path.join(batch_path, 'other_exception.txt')):
                os.remove(os.path.join(batch_path, 'other_exception.txt'))
            if os.path.exists(os.path.join(batch_path, 'properties.pbf')):
                os.remove(os.path.join(batch_path, 'properties.pbf'))
            logger.info("Running essential.over_write_csv")
            essential.over_write_csv(os.path.join(batch_path, 'input_file.txt'), input_list)

        logger.info("Checking if we are running vbscript or python script")
        # Checking if we are running vbscript or python script
        if ".vbs" in str(script_path).lower():
            vb_spider = "E:\\Panacea\\files\\vb_spider.py"
            copy2(vb_spider, os.path.join(batch_path, 'spider.py'))
            copy2(script_path, os.path.join(batch_path, 'vbtopy.vbs'))
        else:
            copy2(script_path, os.path.join(batch_path, 'spider.py'))
        copy2(proxies_path, os.path.join(batch_path, 'proxy.pbf'))
        # copy2(status.property['main_file'], batch_path)
        # copy2(status.property['general_file'], batch_path)

        # batch_local_path = 'E:\\Panacea\\Team_data\\' + str(team_name) + '\\' + str(batch_name)
        batch_property_path = os.path.join(batch_path, 'properties.pbf')
        property_data_for_batch = []
        # property_data_for_batch.append(['project_name=' + str(batch_local_path)])
        # property_data_for_batch.append(['region=DE'])
        for key, val in batch_property.items():
            property_data_for_batch.append([str(key)+'='+str(val)])
        property_data_for_batch.append(['number_of_threads=' + str(num_of_threads_for_this_server)])
        # property_data_for_batch.append(['num_of_attempts=' + str(num_of_attempts)])
        # property_data_for_batch.append(['time_out=' + str(time_out)])
        logger.info("Running essential.over_write_csv")
        essential.over_write_csv(batch_property_path, property_data_for_batch)

        return batch_path.replace(panacea_path, 'E:\\Panacea')

    # This function is executing the crawling script on each server
    @staticmethod
    def run_on_server(batch_id, batch_run_id, server, batch_name, team_name, logger):
        # print(input_list)
        server_con_details = server
        server_name = server_con_details[0]
        server_ip = server_con_details[1]
        server_username = 'panacea'
        server_password = 'eclerx#123'
        panacea_path = 'E:\\panacea\\Team_data'
        remote_path = '\\\\{}\\e$\\panacea\\Team_data'.format(server_ip)
        batch_path = os.path.join(panacea_path, str(team_name), str(batch_name))
        remote_batch_path = os.path.join(remote_path, str(team_name), str(batch_name))
        print(batch_path)
        # print('Starting server - ', str(server_name))
        pythoncom.CoInitialize()
        try:
            logger.info("Establishing connection to " + str(server_ip))
            print("Establishing connection to " + str(server_ip))
            connection = wmi.WMI(server_ip, user=server_username, password=server_password)
            # logger.info("Connection established")
            print("Connection established")
        except wmi.x_wmi as e:
            logger.error(str(e))
            logger.error("Your Username and Password of " + getfqdn(server_ip) + " are wrong.")
            print("Your Username and Password of " + getfqdn(server_ip) + " are wrong.")
            return
        try:
            working_directory = str(batch_path)
            process_id, result = connection.Win32_Process.Create(
                CommandLine='c:\\python36\\python spider.py ' + str(batch_run_id),
                CurrentDirectory=working_directory)
            print(process_id)
            logger.info("Process id - "+str(process_id))
            while True:
                time.sleep(2)
                process_found = paused_forced = False
                try:
                    status = essential.get_status(batch_id)
                    if status in ['paused','forced']:
                        paused_forced = True
                    # logger.info("fetching processes " + str(server_name))
                    all_process = connection.Win32_Process(ProcessId=process_id)
                    # logger.info("processes :" + str(len(all_process)))
                    for process in all_process:
                        # print(process.ProcessId, process.Name)
                        if process_id == process.ProcessId:
                            process_found = True
                            # logger.info("Process running on " + str(server_name))
                            # print('checking')
                            if status == 'paused':
                                logger.info("stopping thread process on server" + str(server_name))
                                print('stopping thread process on server' + str(server_name))
                                with open(os.path.join(remote_batch_path, 'properties.pbf'), 'r+') as fr:
                                    data = fr.readlines()
                                    for i, line in enumerate(data):
                                        if line.split('=')[0] == 'stop':
                                            data[i] = 'stop=1'
                                with open(os.path.join(remote_batch_path, 'properties.pbf'), 'w') as fr:
                                    fr.write(''.join([i for i in data]))
                            if status == 'forced':
                                process.Terminate()
                                # connection.Win32_Process(ProcessId=process_id).Terminate()
                                # process_id, result = connection.Win32_Process.Create(
                                #     CommandLine='cmd.exe /c taskkill /im python.exe /f',
                                #     CurrentDirectory=working_directory)
                                # process_id, result = connection.Win32_Process.Create(
                                #     CommandLine='cmd.exe /c taskkill /pid ' + str(process_id) + ' /f',
                                #     CurrentDirectory=working_directory)
                                time.sleep(2)

                            time.sleep(1)
                            break
                    completed = True
                    if not all_process and not paused_forced:
                        logger.info("Validating completion on server")
                        print("Validating completion on server")
                        input_url = general.read_csv(os.path.join(remote_batch_path, 'input_file.txt'), skip_header=True,encoding='utf8')
                        crawled_url = general.read_csv(os.path.join(remote_batch_path,'input_crawled.txt'),encoding='utf8')
                        for url in input_url:
                            if url not in crawled_url:
                                completed = False
                                logger.info("Not completed")
                                print("Not completed")
                                break
                        if not completed:
                            process_id, result = connection.Win32_Process.Create(
                                CommandLine='c:\\python36\\python spider.py ' + str(batch_run_id),
                                CurrentDirectory=working_directory)
                            print(process_id)
                            logger.info("Resuming Failed batch. Process id - " + str(process_id))
                    if not process_found and completed:
                        Batch.active_servers -=1
                        logger.info("Process completed on " + str(server_name))
                        logger.info("Remaing Active server: " + str(Batch.active_servers))
                        break
                except Exception as e:
                    # print('Exception while looking for process in: ' + str(server_name) + str(e))
                    logger.info('Exception while looking for process in: ' + str(server_name) + str(e))


            # try:
            #     process_id, result = connection.Win32_Process.Create(
            #         CommandLine='cmd.exe /c taskkill /im chrome.exe /f',
            #         CurrentDirectory=working_directory)
            #     process_id, result = connection.Win32_Process.Create(
            #         CommandLine='cmd.exe /c taskkill /im chromedriver.exe /f',
            #         CurrentDirectory=working_directory)
            # except Exception as e:
            #     print(e)
        except Exception as e:
            print(e)
            logger.error(e)

    # This function will generate the final report
    @staticmethod
    def generate_report(ins_backup_paths, team_name, batch_name, batch_id):
        print('generating report for - ' + str(batch_name) + ' for Team - ' + str(team_name))
        ins_backup_paths = ins_backup_paths.split("|")
        df_out_file = pd.DataFrame()
        df_pnf_file = pd.DataFrame()
        df_tag_failed_file = pd.DataFrame()
        df_proxy_blocked_file = pd.DataFrame()
        df_other_file = pd.DataFrame()
        for batch_path in ins_backup_paths:
            print(batch_path)
            # server_con_details = each_server_local
            # server_name = server_con_details[0]
            # server_ip = server_con_details[1]
            # server_username = server_con_details[2]
            # server_password = server_con_details[3]
            # num_of_threads_for_this_server = server_con_details[4]
            # batch_path = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name) + '\\' + str(batch_name) + '\\backup\\' + str(ins_backup_path)

            server_batch_out_file = str(batch_path) + '\\final_data.txt'
            if os.path.isfile(server_batch_out_file):
                # df_out_file = df_out_file.append(essential.read_dataframe(server_batch_out_file, header=True))
                essential.push_data_to_db("found", server_batch_out_file)
            server_batch_pnf_file = str(batch_path) + '\\pnf.txt'
            if os.path.isfile(server_batch_pnf_file):
                # df_pnf_file = df_pnf_file.append(essential.read_dataframe(server_batch_pnf_file, header=True))
                essential.push_data_to_db("pnf", server_batch_pnf_file)
            server_batch_tag_failed_file = str(batch_path) + '\\tag_failed.txt'
            if os.path.isfile(server_batch_tag_failed_file):
                # df_tag_failed_file = df_tag_failed_file.append(essential.read_dataframe(server_batch_tag_failed_file, header=True))
                essential.push_data_to_db("tag_failed", server_batch_tag_failed_file)
            server_batch_proxy_blocked_file = str(batch_path) + '\\proxy_blocked.txt'
            if os.path.isfile(server_batch_proxy_blocked_file):
                # df_proxy_blocked_file = df_proxy_blocked_file.append(essential.read_dataframe(server_batch_proxy_blocked_file, header=True))
                essential.push_data_to_db("proxy_blocked", server_batch_proxy_blocked_file)
            server_batch_other_file = str(batch_path) + '\\other_exception.txt'
            if os.path.isfile(server_batch_other_file):
                # df_other_file = df_other_file.append(essential.read_dataframe(server_batch_other_file, header=True))
                essential.push_data_to_db("other_exception", server_batch_other_file)

        batch_out_location = status.current_path + '/Team_data/' + str(team_name) + '/Batches/' + str(
            batch_name) + '/' + str(datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S"))
        if not os.path.isdir(batch_out_location):
            os.mkdir(batch_out_location)

        # rounding all numbers to five
        df_out_file = df_out_file.round(5)
        df_pnf_file = df_pnf_file.round(5)
        df_tag_failed_file = df_tag_failed_file.round(5)
        df_proxy_blocked_file = df_proxy_blocked_file.round(5)
        df_other_file = df_other_file.round(5)

        batch_out_file_path_on_tool = batch_out_location + '/final_data.txt'
        essential.write_dataframe(df_out_file, batch_out_file_path_on_tool)
        batch_pnf_file_path_on_tool = batch_out_location + '/pnf.txt'
        essential.write_dataframe(df_pnf_file, batch_pnf_file_path_on_tool)
        batch_tag_failed_file_path_on_tool = batch_out_location + '/tag_failed.txt'
        essential.write_dataframe(df_tag_failed_file, batch_tag_failed_file_path_on_tool)
        batch_proxy_blocked_file_path_on_tool = batch_out_location + '/proxy_blocked.txt'
        essential.write_dataframe(df_proxy_blocked_file, batch_proxy_blocked_file_path_on_tool)
        batch_other_file_path_on_tool = batch_out_location + '/other_exception.txt'
        essential.write_dataframe(df_other_file, batch_other_file_path_on_tool)

        essential.update_report_location(batch_id, batch_out_location)

    # This function will create backup and clean the batch to be fit for running again
    @staticmethod
    def clean_batch_process(batch_id, server_details, team_name, batch_name):
        ins_backup_paths = []
        for each_server_local in server_details:
            server_con_details = each_server_local
            server_name = server_con_details[0]
            # server_ip = server_con_details[1]
            # server_username = server_con_details[2]
            # server_password = server_con_details[3]
            # num_of_threads_for_this_server = server_con_details[4]
            server_batch_path = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
                team_name) + '\\' + str(batch_name)
            # server_batch_out_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\final_data.txt'
            # server_batch_input_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\input_file.txt'
            # server_batch_input_crawled_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\input_crawled.txt'
            # server_batch_status_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\crawling_status.pbf'
            # server_batch_pnf_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\pnf.txt'
            # server_batch_proxy_blocked_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\proxy_blocked.txt'
            # server_batch_other_exception_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\other_exception.txt'
            # server_batch_tag_failed_file = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
            #     team_name_for_batch) + '\\' + str(batch_name_local) + '\\tag_failed.txt'
            batch_backup_path = os.path.join(server_batch_path, 'backup')
            if not os.path.exists(batch_backup_path):
                os.makedirs(batch_backup_path)
            timestr = time.strftime("%Y%m%d-%H%M%S")
            ins_backup_path = os.path.join(batch_backup_path, timestr)
            ins_backup_paths.append(str(ins_backup_path))
            if not os.path.exists(ins_backup_path):
                os.makedirs(ins_backup_path)
            if os.path.exists(os.path.join(server_batch_path, 'final_data.txt')):
                copy2(os.path.join(server_batch_path, 'final_data.txt'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'final_data.txt'))
            if os.path.exists(os.path.join(server_batch_path, 'input_file.txt')):
                copy2(os.path.join(server_batch_path, 'input_file.txt'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'input_file.txt'))
            if os.path.exists(os.path.join(server_batch_path, 'input_crawled.txt')):
                copy2(os.path.join(server_batch_path, 'input_crawled.txt'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'input_crawled.txt'))
            if os.path.exists(os.path.join(server_batch_path, 'crawling_status.pbf')):
                copy2(os.path.join(server_batch_path, 'crawling_status.pbf'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'crawling_status.pbf'))
            if os.path.exists(os.path.join(server_batch_path, 'pnf.txt')):
                copy2(os.path.join(server_batch_path, 'pnf.txt'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'pnf.txt'))
            if os.path.exists(os.path.join(server_batch_path, 'proxy_blocked.txt')):
                copy2(os.path.join(server_batch_path, 'proxy_blocked.txt'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'proxy_blocked.txt'))
            if os.path.exists(os.path.join(server_batch_path, 'other_exception.txt')):
                copy2(os.path.join(server_batch_path, 'other_exception.txt'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'other_exception.txt'))
            if os.path.exists(os.path.join(server_batch_path, 'tag_failed.txt')):
                copy2(os.path.join(server_batch_path, 'tag_failed.txt'), ins_backup_path)
                if not essential.get_status(batch_id) in ['paused', 'forced']:
                    os.remove(os.path.join(server_batch_path, 'tag_failed.txt'))
            if os.path.exists(os.path.join(server_batch_path, 'properties.pbf')):
                copy2(os.path.join(server_batch_path, 'properties.pbf'), ins_backup_path)
                os.remove(os.path.join(server_batch_path, 'properties.pbf'))
        ins_backup_paths = "|".join(ins_backup_paths)
        essential.update_server_report(batch_id, ins_backup_paths)
        return ins_backup_paths

