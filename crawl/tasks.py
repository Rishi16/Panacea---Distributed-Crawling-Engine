from __future__ import absolute_import
from crawl.Backbone import wmi
import pythoncom
import logging
import os
import threading
from celery import shared_task
from crawl.Backbone import batch
from crawl.Backbone import essential
from crawl.Backbone import status
from crawl.Backbone.log_writer import log_Writer
import zipfile
import datetime
from crawl.models import db_batch, db_batch_run, db_script
from subprocess import Popen, PIPE


def zip(src, dst, batch_name):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            if ".zip" in filename:
                continue
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            arcname = os.path.join(batch_name, arcname)
            print('zipping %s as %s' % (os.path.join(dirname, filename), arcname))
            zf.write(absname, arcname)
    zf.close()


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
def generate_batch_report(ins_backup_paths, team_name, batch_name, batch_id, batch_run_id):
    msg = "Unknown error"
    report_status = db_batch_run.objects.get(id=batch_run_id).report
    if report_status:
        msg = "Report has already been generated"
        return msg
    print('generating report for - ' + str(batch_name) + ' for Team - ' + str(team_name))
    ins_backup_paths = ins_backup_paths.split("|")
    for batch_path in ins_backup_paths:
        print(batch_path)

    file_path = create_output_files(batch_id, batch_run_id, batch_name, team_name)
    essential.update_report_value(batch_id, file_path, True)
    print("Report generation completed")
    msg = "Report generation completed"
    return msg


def server_usage(server_details):
    server_details = server_details.split('|')
    server_details = [[temp.split(':')[0], temp.split(':')[1], temp.split(':')[2]] for temp in server_details]
    server_username = 'panacea'
    server_password = 'eclerx#123'
    threads = [None] * len(server_details)
    usage_list = [None] * len(server_details)

    def usage(server, usage_list, i):
        server_name, server_ip = server[0], server[1]
        print('usage:', server_name)
        pythoncom.CoInitialize()
        c = wmi.WMI(server_ip, user=server_username, password=server_password, find_classes=False)
        utilizations = [cpu.LoadPercentage for cpu in c.Win32_Processor()]
        cpu = int(sum(utilizations) / len(utilizations))  # avg all cores/processors
        ram = int([mem.AvailableMBytes for mem in c.Win32_PerfFormattedData_PerfOS_Memory()][0])
        ram_pct = int([mem.PercentCommittedBytesInUse for mem in c.Win32_PerfFormattedData_PerfOS_Memory()][0])
        usage_list[i] = {'server_name': server_name, 'cpu': cpu, 'ram': ram, 'ram_pct': ram_pct}
        print('usage:', server_name)

    for i, server in enumerate(server_details):
        threads[i] = threading.Thread(target=usage, args=(server, usage_list, i))
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join()
    return usage_list


def generate_batch_report_old(ins_backup_paths, team_name, batch_name, batch_id, batch_run_id):
    msg = "Unknown error"
    report_status = db_batch_run.objects.get(id=batch_run_id).report
    if report_status:
        msg = "Report has already been generated"
        return msg
    print('generating report for - ' + str(batch_name) + ' for Team - ' + str(team_name))
    ins_backup_paths = ins_backup_paths.split("|")
    for batch_path in ins_backup_paths:
        print(batch_path)
        server_batch_out_file = str(batch_path) + '\\final_data.txt'
        if os.path.isfile(server_batch_out_file):
            try:
                essential.push_data_to_db("found", server_batch_out_file)
                print("cursor here")
                server_run_path = os.path.abspath(os.path.join(batch_path, os.pardir))
                server_run_path = os.path.abspath(os.path.join(server_run_path, os.pardir))
                essential.delete_data_files(os.path.join(server_run_path, "final_data.txt"))
            except Exception as e:
                print(e)
                return str(e)
        server_batch_pnf_file = str(batch_path) + '\\pnf.txt'
        if os.path.isfile(server_batch_pnf_file):
            try:
                essential.push_data_to_db("pnf", server_batch_pnf_file)
                server_run_path = os.path.abspath(os.path.join(batch_path, os.pardir))
                server_run_path = os.path.abspath(os.path.join(server_run_path, os.pardir))
                essential.delete_data_files(os.path.join(server_run_path, "pnf.txt"))
            except Exception as e:
                print(e)
                return str(e)
        server_batch_tag_failed_file = str(batch_path) + '\\tag_failed.txt'
        if os.path.isfile(server_batch_tag_failed_file):
            try:
                essential.push_data_to_db("tag_failed", server_batch_tag_failed_file)
                server_run_path = os.path.abspath(os.path.join(batch_path, os.pardir))
                server_run_path = os.path.abspath(os.path.join(server_run_path, os.pardir))
                essential.delete_data_files(os.path.join(server_run_path, "tag_failed.txt"))
            except Exception as e:
                print(e)
                return str(e)
        server_batch_proxy_blocked_file = str(batch_path) + '\\proxy_blocked.txt'
        if os.path.isfile(server_batch_proxy_blocked_file):
            try:
                essential.push_data_to_db("proxy_blocked", server_batch_proxy_blocked_file)
                server_run_path = os.path.abspath(os.path.join(batch_path, os.pardir))
                server_run_path = os.path.abspath(os.path.join(server_run_path, os.pardir))
                essential.delete_data_files(os.path.join(server_run_path, "proxy_blocked.txt"))
            except Exception as e:
                print(e)
                return str(e)
        server_batch_other_file = str(batch_path) + '\\other_exception.txt'
        if os.path.isfile(server_batch_other_file):
            try:
                essential.push_data_to_db("other_exception", server_batch_other_file)
                server_run_path = os.path.abspath(os.path.join(batch_path, os.pardir))
                server_run_path = os.path.abspath(os.path.join(server_run_path, os.pardir))
                essential.delete_data_files(os.path.join(server_run_path, "other_exception.txt"))
            except Exception as e:
                print(e)
                return str(e)

    file_path = create_output_files(batch_id, batch_run_id, batch_name, team_name)
    essential.update_report_value(batch_id, file_path, True)
    print("Report generation completed")
    msg = "Report generation completed"
    return msg


def create_output_files(batch_id, batch_run_id, batch_name, team_name):
    file_path = essential.generate_output_files(batch_id, batch_run_id, batch_name, team_name)
    zip(file_path, os.path.join(file_path, batch_name), batch_name)
    # zip_file = zipfile.ZipFile('temp.zip', 'w')
    # zip_file.write('temp.txt', compress_type=zipfile.ZIP_DEFLATED)
    # zip_file.close()
    return file_path


def schedule_batch2(batch_id, batch_run_id, batch_name, region, team_name, input_file, supplier_id, user_id,
                    scheduled_date, scheduled_time):
    # Code below is responsible for batch scheduling --- Directly taken from Backbone module
    try:
        log_path = os.path.join("E:", "panacea", "team_data", str(team_name), "Batches", str(batch_name), "logs",
                                str('batch.log'))
        print(log_path)
        logging.basicConfig(filename=log_path,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        logger = logging.getLogger(str(user_id))
    except Exception as e:
        print(e)
        return "Failed"
    try:
        logger.info("-------------- Starting Batch --------------")
        # current_path = os.path.dirname(os.path.abspath(__file__))
        properties_file = status.current_path + '/properties.pbf'
        property = essential.read_properties(properties_file)
        status.property = property
        async_path = os.path.join(status.backbone_path, "async.py")
        print(async_path)
    except Exception as e:
        print(e)
        return "Failed"

    process = Popen(['c:\\python36\\panacea_python.bat', str(team_name) + "_" + str(batch_name), async_path, 'schedule',
                     str(batch_id), str(batch_run_id), str(batch_name), str(region), str(team_name), str(input_file),
                     str(supplier_id), str(user_id), str(scheduled_date), str(scheduled_time)], stdout=PIPE,
                    stderr=PIPE)
    # stdout, stderr = process.communicate()
    return "Success"


def get_or_create_task_logger(team_name, batch_name):
    """ A helper function to create function specific logger lazily. """

    # https://docs.python.org/2/library/logging.html?highlight=logging#logging.getLogger
    # This will always result the same singleton logger
    # based on the task's function name (does not check cross-module name clash,
    # for demo purposes only)
    log_path = os.path.join("E:\\panacea", "team_data", str(team_name), "Batches", str(batch_name), "logs",
                            str('batch.log'))
    logger = logging.getLogger(batch_name)

    # Add our custom logging handler for this logger only
    # You could also peek into Celery task context variables here
    #  http://celery.readthedocs.org/en/latest/userguide/tasks.html#context
    if len(logger.handlers) == 0:
        # Log to output file based on the function name
        hdlr = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)

    return logger


def create_local_folders(batch_data, team_name):
    base_address = status.current_path
    print("==================", base_address)
    batch_name = batch_data
    # Create team_data directory if not exist
    team_data_address = os.path.join(base_address, 'team_data')
    if not os.path.isdir(team_data_address):
        os.mkdir(team_data_address)
    # Create team directory if not exist
    team_address = os.path.join(team_data_address, team_name)
    if not os.path.isdir(team_address):
        os.mkdir(team_address)
    # Create batches directory if not exist
    batches_address = os.path.join(team_address, 'Batches')
    if not os.path.isdir(batches_address):
        os.mkdir(batches_address)
    # Create logs directory if not exist
    logs_address = os.path.join(team_address, 'logs')
    if not os.path.isdir(logs_address):
        os.mkdir(logs_address)
    # Create Proxies directory if not exist
    # Proxies_address = os.path.join(team_address, 'Proxies')
    # if not os.path.isdir(Proxies_address):
    #     os.mkdir(Proxies_address)
    # # Create Scripts directory if not exist
    # Scripts_address = os.path.join(team_address, 'Scripts')
    # if not os.path.isdir(Scripts_address):
    #     os.mkdir(Scripts_address)
    # # Create Servers directory if not exist
    # Servers_address = os.path.join(team_address, 'Servers')
    # if not os.path.isdir(Servers_address):
    #     os.mkdir(Servers_address)
    # # Create batches_to_run file if not exist
    # batches_to_run_address = os.path.join(team_address, 'batches_to_run.pbf')
    # if not os.path.isfile(batches_to_run_address):
    #     essential.over_write_file(batches_to_run_address, '')
    # # Create batches_to_stop file if not exist
    # batches_to_stop_address = os.path.join(team_address, 'batches_to_stop.pbf')
    # if not os.path.isfile(batches_to_stop_address):
    #     essential.over_write_file(batches_to_stop_address, '')
    # Create batch-name directory if not exist
    batch_address = os.path.join(batches_address, batch_name)
    if not os.path.isdir(batch_address):
        os.mkdir(batch_address)
    # Create batch-logs directory if not exist
    batch_logs_address = os.path.join(batch_address, 'logs')
    if not os.path.isdir(batch_logs_address):
        os.mkdir(batch_logs_address)

    # batch_property_address = os.path.join(batch_address, 'properties.pbf')
    # property_data_for_batch = []
    # # property_data_for_batch.append(['project_name=' + str(batch_local_path)])
    # property_data_for_batch.append(['input_file=' + str(input_file_name)])
    # property_data_for_batch.append(['script=' + str(script_name)])
    # property_data_for_batch.append(['proxies=' + str(proxies_file_name)])
    # property_data_for_batch.append(['servers=' + str(server_file_name)])
    # property_data_for_batch.append(['region=' + str(region)])
    # property_data_for_batch.append(['num_of_attempts=' + str(num_of_attempts)])
    # property_data_for_batch.append(['time_out=' + str(time_out)])
    # property_data_for_batch.append(['crawler_type=' + str(crawler_type)])
    # essential.over_write_csv(batch_property_address, property_data_for_batch)


@shared_task
def schedule_batch(batch_id, batch_name, region, team_name, input_file, supplier_id, user_id, scheduled_date,
                   scheduled_time, resume=False, restart=False):
    try:
        status.init()  # This will initialize all the status variables and global variables
        properties_file = status.current_path + '/properties.pbf'
        property = essential.read_properties(properties_file)
        status.property = property
        create_local_folders(batch_name, team_name)
        logger = get_or_create_task_logger(team_name, batch_name)
        # log_path = os.path.join("E:\\panacea", "team_data", str(team_name), "Batches", str(batch_name), "logs",
        #                         str('batch.log'))
        # logger = get_task_logger(log_path)
        # Code below is responsible for batch scheduling --- Directly taken from Backbone module

        # base_address = status.current_path
        supplier_name, script_file_path, proxy_file_path, server_details, num_of_attempts, time_out = get_batch_data(
            supplier_id)

        batch_to_run = batch.Batch()
        if resume:
            batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
            if batch_run:
                current_batch_run = batch_run[0]
        else:
            current_batch_run = db_batch_run.objects.create(batch_id=batch_id)
        batch_to_run.start(batch_id, current_batch_run.id, batch_name, region, team_name, user_id, input_file,
                           script_file_path, proxy_file_path, server_details, num_of_attempts, time_out, logger)
    except Exception as e:
        print(e)


@shared_task
def generate_batch_report2(batch_id, batch_name, team_name, server_report):
    # Code below is responsible for batch scheduling --- Directly taken from Backbone module
    try:
        status.init()  # This will initialize all the status variables and global variables
        main_log_file = status.current_path + '/logs/main_logs.log'
        mainlog = log_Writer(main_log_file)
    except Exception as e:
        print(e)
        return "Failed"
    try:
        batch_to_generate_report = batch.Batch()
        batch_to_generate_report.generate_report(server_report, team_name, batch_name, batch_id)
    except Exception as e:
        mainlog.write('Batch Exception - ' + str(e) + ' - ' + str(team_name) + ' - ' + str(batch_name) + ' - ' + str(
            datetime.datetime.now()))  # Writing main logs


@shared_task
def testing_task():
    with open("E:\\Harsh\\python_projects\\aa.txt", 'a+') as f:
        f.write("aa\r\n")
