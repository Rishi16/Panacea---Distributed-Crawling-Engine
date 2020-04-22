"""
Author: Harsh Dubey
Windows Remote Connection Library: WMI

This is the starting point for execution
Other related scripts -
    team.py
    batch.py
    status.py
    log_writer.py
    check_ram.py
    essential.py
(Please feel free to use this code for personal use only without changing it or its functionality)
"""

import threading
import time
import essential
import datetime
import status
from log_writer import log_Writer
from team import Team
import sys

#----------This main loop will always run and will keep on creating new threads for new teams---------#
try:
    status.init()  # This will initialize all the status variables and global variables
    main_log_file = status.current_path + '/logs/main_logs.log'
    mainlog = log_Writer(main_log_file)
except Exception as e:
    print(e)
    sys.exit()
try:
    print('-------------- Initializing System --------------')

    # current_path = os.path.dirname(os.path.abspath(__file__))
    properties_file = status.current_path + '/properties.pbf'
    property = essential.read_properties(properties_file)
    status.property = property

    mainlog.write('System Initialized - ' + str(datetime.datetime.now()))   # Writing main logs

    # Infinite loop for the application
    while(True):
        time.sleep(int(status.property['main_loop_sleep']))
        team_data = essential.file_to_list(status.property['team_data'])
        team_data_to_stop = essential.file_to_list(status.property['team_data_to_stop'])
        # Loop through all the teams available in the queue - Team_data.pbf
        for each_team in team_data:
            # thread_name = essential.get_team_name(each_team)
            thread_name = each_team
            # Check if the team crawling has been stopped by finding it in - team_data_to_stop.pbf
            if each_team in team_data_to_stop:
                if each_team in status.team_status and status.team_status[each_team] != 'stop':
                    mainlog.write('Found Team in team_data_to_stop.pbf - ' + str(each_team) + ' - ' + str(datetime.datetime.now())) # Writing main logs
                    mainlog.write('Stopping the services for Team - ' + str(each_team) + ' - ' + str(datetime.datetime.now()))  # Writing main logs
                    status.team_status[thread_name] = 'stop'
                    # Continue will bypass the process of starting the services for this team
                continue

            # If the services for a team are not started already then this will get triggered
            if each_team not in status.team_in_system:
                mainlog.write('Found Team in team_data.pbf. Starting services for it. - ' + str(each_team) + ' - ' + str(datetime.datetime.now()))  # Writing main logs
                status.team_in_system.append(each_team)
                # Start a new thread for this new team
                if thread_name != '':
                    status.team_status[thread_name] = 'running'
                    t = threading.Thread(target=Team.start, name=thread_name, args=[each_team])
                    t.daemon = True
                    t.start()
                    mainlog.write('Team services started successfully - ' + str(each_team) + ' - ' + str(datetime.datetime.now()))  # Writing main logs
                # if the team name is not defined properly in - Team_data.pbf
                else:
                    mainlog.write('Issue is starting Team servies. Please check Team_data.pbf - ' + str(each_team) + ' - ' + str(datetime.datetime.now()))  # Writing main logs
                    print('Could not start the process for team with no name')
except Exception as e:
    mainlog.write(str(e) + ' - ' + str(datetime.datetime.now()))  # Writing main logs
    print(e)
