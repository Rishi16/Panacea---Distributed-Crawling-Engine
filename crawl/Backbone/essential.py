import csv
import os
import datetime
import ast
import pandas as pd
import codecs
import select
import psycopg2.extensions
import psycopg2
from crawl.models import db_batch, db_batch_run, db_script, datasource_found, datasource_pnf, datasource_proxy_blocked, datasource_tag_failed, datasource_other_exception

def read_properties(file_name):
    property = {}
    with open(file_name, 'rt') as f:
        for line in f:
            line = line.replace('\n', '')
            values = line.split("=")
            property[values[0]] = values[1]
    return property

def file_to_list(file_name):
    results = []
    with open(file_name, 'rt') as f:
        for line in f:
            line = line.replace('\n', '')
            # values = line.split("|")
            results.append(line)
    return results

def pipe_to_list(server_details):
    server_details = server_details.split('|')
    server_details = [[temp.split(':')[0], temp.split(':')[1], temp.split(':')[2]] for temp in server_details]
    return server_details

def get_team_name(each_team_data):
    current_path = os.path.dirname(os.path.abspath(__file__))
    properties_file = current_path + '\\properties.pbf'
    property = read_properties(properties_file)
    data_values = each_team_data.split('\t')
    if int(property['total_values_in_team_data']) > 0:
        if len(data_values) == int(property['total_values_in_team_data']):
            return data_values[0]
        else:
            return ''
    else:
        return ''

# Write data to file
def write_file(path, data, encoding='utf-8'):
    with codecs.open(path, 'a+', encoding=encoding) as f:
        f.write(data+'\r\n')

# Overwrite data to file
def over_write_file(path, data, encoding='utf-8'):
    with codecs.open(path, 'w', encoding=encoding) as f:
        f.write(data+'\r\n')

# Read data from to file
def read_file(path, encoding='utf-8'):
    with codecs.open(path, 'r+', encoding=encoding) as f:
        data = f.read()
    return data

def get_batches(team_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    properties_file = current_path + '\\properties.pbf'
    property = read_properties(properties_file)
    team_data_folder = os.path.join(current_path, str(property['team_data_folder']))
    current_team_folder = os.path.join(team_data_folder, team_name)
    current_team_batch_folder = os.path.join(current_team_folder, 'Batches')
    all_batch_name = []
    for batch_name in os.listdir(current_team_batch_folder):
        if os.path.isdir(os.path.join(current_team_batch_folder, batch_name)):
            all_batch_name.append(batch_name)
    return all_batch_name

def read_proxies(file_name):
    proxies = []
    each_proxy = {}
    with open(file_name, 'rt') as f:
        validator = 0
        for line in f:
            validator+=1
            line = line.replace('\n', '')
            values = line.split("=")
            if (validator == 1):
                each_proxy['host'] = values[1]
            elif (validator == 2):
                each_proxy['username'] = values[1]
            elif (validator == 3):
                each_proxy['password'] = values[1]
            if (validator == 4):
                each_proxy['port'] = values[1]

            if validator == 4:
                validator = 0
                proxies.append(each_proxy)
                each_proxy = {}
    return proxies

def get_csv_size(file_path):
    csv.register_dialect('myDialect', delimiter='\t')
    with open(file_path, "r") as f:
        reader = csv.reader(f, dialect='myDialect')
        data = list(reader)
        row_count = len(data)
    return row_count

def get_csv_rows(file_path, start_row, end_row):
    csv.register_dialect('myDialect', delimiter='\t')
    with open(file_path, "r") as f:
        reader = csv.reader(f, dialect='myDialect')
        interestingrows = [row for idx, row in enumerate(reader) if idx in range(start_row, end_row)]
    return interestingrows

def distribute_input(file_path, server_details, batch_id):
    # Old logic to distribute inputs equaly
    # num_of_servers = len(server_details)
    # all_servers_dist = []
    # csv.register_dialect('myDialect', delimiter='\t')
    # with open(file_path, "r") as f:
    #     reader = csv.reader(f, dialect='myDialect')
    #     data = list(reader)
    #     row_count = len(data)
    #     per_server_division_round_off_count = int(row_count / num_of_servers)
    #     last_division_extra_count = row_count - (per_server_division_round_off_count * num_of_servers)
    #     start_limit = 0
    #     end_limit = 0
    #     for each_server in range(0, num_of_servers):
    #         start_limit = end_limit
    #         if each_server == num_of_servers - 1:
    #             end_limit = end_limit + per_server_division_round_off_count + last_division_extra_count
    #         else:
    #             end_limit = end_limit + per_server_division_round_off_count
    #         interestingrows = data[start_limit:end_limit]
    #         all_servers_dist.append(interestingrows)
    # return row_count, all_servers_dist

    # New logic to distribute inputs on the basis of threads
    num_of_servers = len(server_details)
    list_of_threads = []
    list_of_threads.extend([int(each_server[2].split('-')[0]) for each_server in server_details])
    list_of_contribution = []
    for each_thread in list_of_threads:
        list_of_contribution.append( int( (each_thread/sum(list_of_threads))*100 ) )
    contribution_total=sum(list_of_contribution)
    if contribution_total<100:
        list_of_contribution[-1] += (100-contribution_total)
    else:
        list_of_contribution[-1] -= (contribution_total - 100)

    actual_contribution = []
    csv.register_dialect('myDialect', delimiter='\t')
    with codecs.open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, dialect='myDialect')
        data = list(reader)
        header_row = data.pop(0)
        row_count = len(data)
    update_input_count(batch_id, row_count)
    for each_contribution in list_of_contribution:
        actual_contribution.append( int( (each_contribution/100)*row_count ) )

    total_actual_contribution = sum(actual_contribution)
    if total_actual_contribution<row_count:
        actual_contribution[-1] += (row_count-total_actual_contribution)
    else:
        actual_contribution[-1] -= (total_actual_contribution - row_count)
    all_servers_dist = []
    start_limit = 0
    end_limit = 0
    for server_val in range(0, len(server_details)):
        start_limit = end_limit
        end_limit += actual_contribution[server_val]
        interestingrows = data[start_limit:end_limit]
        interestingrows.insert(0, header_row)
        all_servers_dist.append(interestingrows)
    return row_count, all_servers_dist


def write_csv(file_path, data):
    csv.register_dialect('myDialect', delimiter='\t')
    myFile = codecs.open(file_path, 'a+', encoding='utf-8')
    with myFile:
        writer = csv.writer(myFile, dialect='myDialect')
        writer.writerows(data)

def over_write_csv(file_path, data):
    csv.register_dialect('myDialect', delimiter='\t')
    myFile = codecs.open(file_path, 'w', encoding='utf-8')
    with myFile:
        writer = csv.writer(myFile, dialect='myDialect')
        writer.writerows(data)

def read_dataframe(file_path, seperator='\t', header=True):
    if header == True:
        df = pd.read_csv(file_path, sep=seperator,
                          encoding="utf-8", error_bad_lines=False)
    else:
        df = pd.read_csv(file_path, sep=seperator, names = ["comProductURL"], header=None,
                          encoding="utf-8", error_bad_lines=False)
    return df

def write_dataframe(df, file_path, seperator='\t', index=False):
    df.to_csv(file_path, sep=seperator, encoding='utf-8', index=index)


def delete_data_files(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

# These functions are written to query database

def update_batch_completion(batch_id, found, pnf, tag_failed, proxy_blocked, other):
    # t = db_batch.objects.get(id=batch_id)
    t = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
    if t:
        t = t[0]
    data_changed = False
    if found + pnf + tag_failed + proxy_blocked + other > 0:
        t.completion = found + pnf + tag_failed + proxy_blocked + other
        data_changed = True
    if found > 0:
        t.completion_found = found
        data_changed = True
    if pnf > 0:
        t.completion_pnf = pnf
        data_changed = True
    if tag_failed > 0:
        t.completion_tag_failed = tag_failed
        data_changed = True
    if proxy_blocked > 0:
        t.completion_proxy_blocked = proxy_blocked
        data_changed = True
    if other > 0:
        t.completion_other = other
        data_changed = True
    if data_changed:
        t.save()

def update_input_count(batch_id, input_count):
    # t = db_batch.objects.get(id=batch_id)
    t = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
    if t:
        t = t[0]
    t.input_count = input_count
    t.save()
    # db_batch.objects.filter(id=batch_id).update(input_count=input_count)

def update_status(batch_id, status):
    # t = db_batch.objects.get(id=batch_id)
    t = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
    if t:
        t = t[0]
    t.status = status
    t.save()

def get_status(batch_id):
    # t = db_batch.objects.get(id=batch_id)
    t = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
    if t:
        t = t[0]
    return str(t.status)

def update_report_value(batch_id, file_path, report_value):
    # t = db_batch.objects.get(id=batch_id)
    t = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
    if t:
        t = t[0]
    t.report = report_value
    t.report_location = str(file_path)
    t.save()

def update_server_report(batch_id, server_report):
    # t = db_batch.objects.get(id=batch_id)
    t = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
    if t:
        t = t[0]
    t.server_report = server_report
    t.save()

def get_latest_batch_run(batch_id):
    t = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
    if t:
        t = t[0]
    print("Batch run ID for this is - ",t.id)
    return t

def wait(conn):
    while 1:
        state = conn.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        elif state == psycopg2.extensions.POLL_WRITE:
            select.select([], [conn.fileno()], [])
        elif state == psycopg2.extensions.POLL_READ:
            select.select([conn.fileno()], [], [])
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)

def push_data_to_db1(tag, file_path):
    conn = psycopg2.connect("host=localhost dbname=panacea user=postgres password=eclerx##123")
    cur = conn.cursor()
    if tag == "found":
        with codecs.open(file_path, 'r', encoding="utf-8") as f:
            cur.copy_expert("""COPY crawl_datasource_found ("batch_id", "data_value") FROM STDIN WITH (FORMAT CSV)""", f)
        conn.commit()
    elif tag == "pnf":
        with codecs.open(file_path, 'r', encoding="utf-8") as f:
            cur.copy_expert("""COPY crawl_datasource_pnf ("batch_id", "data_value") FROM STDIN WITH (FORMAT CSV)""", f)
        conn.commit()
    elif tag == "tag_failed":
        with codecs.open(file_path, 'r', encoding="utf-8") as f:
            cur.copy_expert("""COPY crawl_datasource_tag_failed ("batch_id", "data_value") FROM STDIN WITH (FORMAT CSV)""", f)
        conn.commit()
    elif tag == "proxy_blocked":
        with codecs.open(file_path, 'r', encoding="utf-8") as f:
            cur.copy_expert("""COPY crawl_datasource_proxy_blocked ("batch_id", "data_value") FROM STDIN WITH (FORMAT CSV)""", f)
        conn.commit()
    else:
        with codecs.open(file_path, 'r', encoding="utf-8") as f:
            cur.copy_expert("""COPY crawl_datasource_other_exception ("batch_id", "data_value") FROM STDIN WITH (FORMAT CSV)""", f)
        conn.commit()

def insert_csv_to_db(conn, cur, table_name, file_object):
    SQL_STATEMENT = """
            COPY %s(batch_run_id, creation_date, data) FROM STDIN WITH
            CSV
            HEADER
            DELIMITER AS '\t'
            """
    cur.copy_expert(sql=SQL_STATEMENT % table_name, file=file_object)
    conn.commit()

def push_data_to_db(tag, file_path):
    print("Started storing in DB")
    cur, conn = ext_connect_postgre()
    if tag == "found":
        print("Storing Found")
        table_name = "crawl_datasource_found"
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            insert_csv_to_db(conn, cur, table_name, f)
        # insert_count = datasource_found.objects.from_csv(file_path, mapping={"batch_run_id": "Batch_run_id", "creation_date": "Creation_date", "data": "Data"}, delimiter="\t", encoding='CP1252')
        # print("{} records inserted in found".format(insert_count))
    elif tag == "pnf":
        print("Storing pnf")
        table_name = "crawl_datasource_pnf"
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            insert_csv_to_db(conn, cur, table_name, f)
        # insert_count = datasource_pnf.objects.from_csv(file_path, mapping={"batch_run_id": "Batch_id", "creation_date": "Creation_date", "data": "Data"}, delimiter="\t", encoding='utf-8')
        # print("{} records inserted in found".format(insert_count))
    elif tag == "proxy_blocked":
        print("Storing proxy_blocked")
        table_name = "crawl_datasource_proxy_blocked"
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            insert_csv_to_db(conn, cur, table_name, f)
        # insert_count = datasource_proxy_blocked.objects.from_csv(file_path, mapping={"batch_run_id": "Batch_id", "creation_date": "Creation_date", "data": "Data"}, delimiter="\t", encoding='utf-8')
        # print("{} records inserted in found".format(insert_count))
    elif tag == "tag_failed":
        print("Storing tag_failed")
        table_name = "crawl_datasource_tag_failed"
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            insert_csv_to_db(conn, cur, table_name, f)
        # insert_count = datasource_tag_failed.objects.from_csv(file_path, mapping={"batch_run_id": "Batch_id", "creation_date": "Creation_date", "data": "Data"}, delimiter="\t", encoding='utf-8')
        # print("{} records inserted in found".format(insert_count))
    else:
        print("Storing other_exception")
        table_name = "crawl_datasource_other_exception"
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            insert_csv_to_db(conn, cur, table_name, f)
        # insert_count = datasource_other_exception.objects.from_csv(file_path, mapping={"batch_run_id": "Batch_id", "creation_date": "Creation_date", "data": "Data"}, delimiter="\t", encoding='utf-8')
        # print("{} records inserted in found".format(insert_count))
    cur.close()
    conn.close()
    print("Completed")

def generate_output_files1(batch_id, batch_run_id, batch_name, team_name):
    current_path = "E:/Panacea"
    return_found = datasource_found.objects.filter(batch_run_id=batch_run_id).order_by('creation_date').values_list('data', flat=True)
    batch_out_location = current_path + '/Team_data/' + str(team_name) + '/Batches/' + str(
        batch_name) + '/' + str(datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S"))
    if not os.path.isdir(batch_out_location):
        os.mkdir(batch_out_location)
    values_list_to_write = []
    values_list_to_write.append(list(return_found[0].keys()))
    for temp_dict in return_found:
        values_list_to_write.append(list(temp_dict.values()))
    write_csv(os.path.join(batch_out_location, "final_data.txt"), values_list_to_write)

    # val_to_return = []
    # for record_val in return_found:
    #     val_to_return.append(record_val.data)

    return return_found

def generate_output_files2(batch_id, batch_run_id, batch_name, team_name):
    current_path = "E:/Panacea"
    batch_out_location = current_path + '/Team_data/' + str(team_name) + '/Batches/' + str(
        batch_name) + '/' + str(datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S"))
    if not os.path.isdir(batch_out_location):
        os.mkdir(batch_out_location)
    return_found = datasource_found.objects.to_csv(
            os.path.join(batch_out_location, "final_data.txt"),
            "data->>'Name'"
        )
    return return_found

def get_field_mapping_query(batch_id):
    script_id = db_batch.objects.get(id=batch_id).script_name_id

    # input field mapping
    # print("aaaaaaaaaaaaa", str(db_script.objects.get(id=script_id).input_field_mapping))
    input_field_mapping = ast.literal_eval(db_script.objects.get(id=script_id).input_field_mapping)
    input_field_mapping_query = ""
    for field in input_field_mapping:
        if input_field_mapping_query == "":
            input_field_mapping_query = input_field_mapping_query + " data->>'" + str(field) + "' as \"" + str(field) + "\""
        else:
            input_field_mapping_query = input_field_mapping_query + ", data->>'" + str(field) + "' as \"" + str(field) + "\""
    # print(input_field_mapping_query)

    # output field mapping
    output_field_mapping = ast.literal_eval(db_script.objects.get(id=script_id).output_field_mapping)
    output_field_mapping_query = ""
    for field in output_field_mapping:
        if output_field_mapping_query == "":
            output_field_mapping_query = output_field_mapping_query + " data->>'" + str(field) + "' as \"" + str(field) + "\""
        else:
            output_field_mapping_query = output_field_mapping_query + ", data->>'" + str(field) + "' as \"" + str(field) + "\""
    # print(output_field_mapping_query)

    return (input_field_mapping_query, output_field_mapping_query)

def ext_connect_postgre():
    conn = psycopg2.connect("dbname = 'panacea' user = 'postgres' host = 'localhost' password = 'eclerx##123'")
    cur = conn.cursor()
    return (cur, conn)


def generate_output_files(batch_id, batch_run_id, batch_name, team_name):
    try:
        thread = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        cur, conn = ext_connect_postgre()
        current_path = "E:/Panacea"
        batch_out_location = current_path + '/Team_data/' + str(team_name) + '/Batches/' + str(
            batch_name) + '/' + str(datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S"))
        if not os.path.isdir(batch_out_location):
            os.mkdir(batch_out_location)
        input_field_mapping_query, output_field_mapping_query = get_field_mapping_query(batch_id)

        # generating final_data file
        SQL_STATEMENT_OUTPUT = "COPY (SELECT" +\
                        str(output_field_mapping_query) +\
                        " FROM crawl_datasource_found where batch_run_id = {}) TO STDIN WITH CSV HEADER DELIMITER AS '\t'".format(batch_run_id)
        with open(os.path.join(batch_out_location, "final_data.txt"), 'wb') as f:
            cur.copy_expert(SQL_STATEMENT_OUTPUT, f)

        # generating pnf file
        SQL_STATEMENT_PNF = "COPY (SELECT" + \
                               str(input_field_mapping_query) + \
                               " FROM crawl_datasource_pnf where batch_run_id = {}) TO STDIN WITH CSV HEADER DELIMITER AS '\t'".format(
                                   batch_run_id)
        with open(os.path.join(batch_out_location, "pnf.txt"), 'wb') as f:
            cur.copy_expert(SQL_STATEMENT_PNF, f)

        # generating tag_failed file
        SQL_STATEMENT_TAG_FAILED = "COPY (SELECT" + \
                               str(input_field_mapping_query) + \
                               " FROM crawl_datasource_tag_failed where batch_run_id = {}) TO STDIN WITH CSV HEADER DELIMITER AS '\t'".format(
                                   batch_run_id)
        with open(os.path.join(batch_out_location, "tag_failed.txt"), 'wb') as f:
            cur.copy_expert(SQL_STATEMENT_TAG_FAILED, f)


        # generating proxy_blocked file
        SQL_STATEMENT_PROXY_BLOCKED = "COPY (SELECT" + \
                               str(input_field_mapping_query) + \
                               " FROM crawl_datasource_proxy_blocked where batch_run_id = {}) TO STDIN WITH CSV HEADER DELIMITER AS '\t'".format(
                                   batch_run_id)
        with open(os.path.join(batch_out_location, "proxy_blocked.txt"), 'wb') as f:
            cur.copy_expert(SQL_STATEMENT_PROXY_BLOCKED, f)


        # generating other_exception file
        SQL_STATEMENT_OTHER_EXCEPTION = "COPY (SELECT" + \
                               str(input_field_mapping_query) + \
                               " FROM crawl_datasource_other_exception where batch_run_id = {}) TO STDIN WITH CSV HEADER DELIMITER AS '\t'".format(
                                   batch_run_id)
        with open(os.path.join(batch_out_location, "other_exception.txt"), 'wb') as f:
            cur.copy_expert(SQL_STATEMENT_OTHER_EXCEPTION, f)
        cur.close()
        conn.close()
    finally:
        psycopg2.extensions.set_wait_callback(thread)
    return batch_out_location