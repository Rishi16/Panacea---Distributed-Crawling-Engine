"""
Author: Harsh Dubey
Windows Remote Connection Library: WMI

(Please feel free to use this code for personal use only without changing it or its functionality)
"""

import threading
import time
import essential
import datetime
import  status
from log_writer import log_Writer
from batch import Batch
import sys

class Team:
    # team_name = ''
    # team_path = ''
    # def __init__(self, team_data):
    #     self.team_data = team_data

    # This function will be responsible for crawling for every team. It will be called for every team seperately
    @staticmethod
    def start(team_data):
        try:
            # team_data_split = team_data.split('\t')
            # team_name = team_data_split[0]
            # team_path = team_data_split[1]
            team_name = team_data
            print(team_name)
            # print(team_path)
            print(team_name, status.team_status[team_name])
            team_log_file = status.current_path + '/Team_data/' + str(team_name) + '/logs/team_logs.log'
            teamlog = log_Writer(team_log_file)
        except Exception as e:
            print(e)
            return
        try:
            print('------- Starting Main service for team - ' + str(team_name) + '-------')
            teamlog.write('Starting Main service for team - ' + str(team_name) + ' - ' + str(datetime.datetime.now())) # Writing team log
            status.batch_in_system[team_name] = []
            status.batch_status[team_name] = {}
            team_batches_to_stop_path = status.current_path + '\\Team_data\\' + str(team_name) + '\\batches_to_stop.pbf'
            team_batches_to_run_path = status.current_path + '\\Team_data\\' + str(team_name) + '\\batches_to_run.pbf'
            # Infinite loop for the Team
            while (True):
                time.sleep(int(status.property['start_crawl_sleep']))
                team_batches_to_stop = essential.file_to_list(team_batches_to_stop_path)
                available_batches = essential.file_to_list(team_batches_to_run_path)

                # This loop will check for all the stopped batches if they need to be restarted from scratch
                for each_batch_status in status.batch_status[team_name]:
                    if each_batch_status not in available_batches:
                        status.batch_status[team_name][each_batch_status] = 'notstarted'

                for each_batch in available_batches:
                    batch_thread_name = str(each_batch) + '_' + str(team_name)
                    # This will stop the batches
                    if each_batch in team_batches_to_stop:
                        if each_batch in status.batch_status[team_name] and status.batch_status[team_name][each_batch] != 'stop':
                            print('batch found in stop batches list')
                            teamlog.write('Batch found in stop batches list - ' + str(team_name) + ' - ' + str(each_batch) + ' - ' + str(datetime.datetime.now())) # Writing team log
                            if each_batch in status.batch_in_system[team_name]:
                                status.batch_in_system[team_name].remove(each_batch)
                            status.batch_status[team_name][each_batch] = 'stop'
                        continue

                    # This will start the batches
                    if each_batch not in status.batch_in_system[team_name]:
                        # check for the time
                        if each_batch in status.batch_status[team_name]:
                            if not status.batch_status[team_name][each_batch] == 'stop':
                                teamlog.write('Running the batch - ' + str(team_name) + ' - ' + str(
                                    each_batch) + ' - ' + str(datetime.datetime.now()))  # Writing team log
                                status.batch_status[team_name][each_batch] = 'running'
                            else:
                                teamlog.write('Re-running the batch - ' + str(team_name) + ' - ' + str(
                                    each_batch) + ' - ' + str(datetime.datetime.now()))  # Writing team log
                                status.batch_status[team_name][each_batch] = 'rerunning'
                        else:
                            teamlog.write('Running the batch - ' + str(team_name) + ' - ' + str(
                                each_batch) + ' - ' + str(datetime.datetime.now()))  # Writing team log
                            status.batch_status[team_name][each_batch] = 'running'
                        print('Batch status - ', status.batch_status[team_name][each_batch])
                        status.batch_in_system[team_name].append(each_batch)

                        t = threading.Thread(target=Batch.start, name=batch_thread_name, args=[each_batch, team_name, batch_thread_name])
                        t.daemon = True
                        t.start()

                # This will stop the team services
                if status.team_status[team_name] == 'stop':
                    print(status.team_status[team_name])
                    teamlog.write('Stopping the services for team - ' + str(team_name) + ' - ' + str(datetime.datetime.now()))  # Writing team log
                    print('Stopping the crawling for team - ' + str(team_name))
                    status.team_in_system.remove(team_data)
                    # We have to write the code to stop the batches as well -----------------------++++++++++++++++++------------------
                    print('All the crawling services for team - ' + str(team_name) + ' have been stopped')
                    break


        except Exception as e:
            teamlog.write(str(e) + ' - ' + str(team_name) + ' - ' + str(datetime.datetime.now())) # Writing team log
