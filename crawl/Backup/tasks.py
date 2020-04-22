from __future__ import absolute_import
import string

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import os
from celery import shared_task
from crawl.Backbone import batch
from crawl.Backbone import essential
from crawl.Backbone import status
from crawl.Backbone.log_writer import log_Writer
import sys
import datetime
# from crawl.models import db_batch, db_script
def get_batch_data(supplier_id):
    obj = db_script.objects.get(id=supplier_id)
    supplier_name = obj.supplier_name
    script_file_path = obj.script_file.name
    proxy_file_path = obj.proxy_file.name
    server_details = obj.servers
    num_of_attempts = obj.attempt
    time_out = obj.timeout
    return (supplier_name, script_file_path, proxy_file_path, server_details, num_of_attempts, time_out)

@shared_task
def schedule_batch(batch_id, batch_name, team_name, input_file, supplier_id, user_id):
    # Code below is responsible for batch scheduling --- Directly taken from Backbone module
    try:
        status.init()  # This will initialize all the status variables and global variables
        main_log_file = status.current_path + '/logs/main_logs.log'
        mainlog = log_Writer(main_log_file)
    except Exception as e:
        print(e)
        return "Failed"
    try:
        print('-------------- Starting Batch --------------')

        # current_path = os.path.dirname(os.path.abspath(__file__))
        properties_file = status.current_path + '/properties.pbf'
        property = essential.read_properties(properties_file)
        status.property = property

        mainlog.write('Batch Creating - ' + str(team_name) + ' - ' + str(batch_name) + ' - ' + str(datetime.datetime.now()))  # Writing main logs
    except Exception as e:
        print(e)
        return "Failed"

    # base_address = status.current_path
    supplier_name, script_file_path, proxy_file_path, server_details, num_of_attempts, time_out = get_batch_data(supplier_id)

    batch_to_run = batch.Batch()
    batch_to_run.start(batch_id, batch_name, team_name, user_id, input_file, script_file_path, proxy_file_path, server_details, num_of_attempts, time_out)
