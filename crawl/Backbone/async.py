import sys
import batch
import essential
import logging

def schedule_batch(batch_id, batch_run_id, batch_name, region, team_name, input_file, supplier_id, user_id, scheduled_date, scheduled_time):
    # Code below is responsible for batch scheduling --- Directly taken from Backbone module
    try:
        status.init()  # This will initialize all the status variables and global variables
        main_log_file = status.current_path + '/logs/main_logs.log'
        mainlog = log_Writer(main_log_file)
    except Exception as e:
        print(e)
        sys.exit(1)
    try:
        print('-------------- Starting Batch --------------')

        # current_path = os.path.dirname(os.path.abspath(__file__))
        properties_file = status.current_path + '/properties.pbf'
        property = essential.read_properties(properties_file)
        status.property = property

        mainlog.write('Batch Creating - ' + str(team_name) + ' - ' + str(batch_name) + ' - ' + str(datetime.datetime.now()))  # Writing main logs
    except Exception as e:
        print(e)
        sys.exit(1)

    # base_address = status.current_path
    supplier_name, script_file_path, proxy_file_path, server_details, num_of_attempts, time_out = get_batch_data(supplier_id)

    batch_to_run = batch.Batch()

    batch_to_run.start(batch_id, batch_run_id, batch_name, region, team_name, user_id, input_file, script_file_path, proxy_file_path, server_details, num_of_attempts, time_out)


args = sys.argv
logging.info("yessss")
if args[0] == "schedule":
    schedule_batch(args[1], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
else:
    print("Invalid argument")
    sys.exit()