import general
import os
from panacea_crawl import spider
import subprocess
current_path = os.path.dirname(os.path.abspath(__file__))


class crawler(spider):

    def __init__(self):
        super().__init__(current_path)
        super().debug(False)
        print('Crawling started')
        # sys.exit()
        general.header_values(["manufacturer", "description", "price", "stock", "partcode", "field0", "field1", "field2", "field3", "field4", "field5", "field6", "field7", "field8", "field9", "field10", "field11", "field12", "field13", "field14", "field15", "field16", "field17", "field18", "field19"])

    def initiate(self, input_row, region, proxies_from_tool,thread_name):
        num_attempt = 1
        file_path = os.path.join(current_path, str(thread_name) + "_support.txt")
        while(num_attempt<10):
            try:
                print('Product crawl')
                if os.path.exists(file_path):
                    os.remove(file_path)
                process = subprocess.Popen(['cscript', 'vbtopy.vbs',
                                            input_row[0],
                                            file_path], stdout=subprocess.PIPE)
                process.wait()
                num_attempt += 1
                if os.path.exists(file_path):
                    break
            except Exception as e:
                print(e)
                self.push_data2("proxy_blocked", [input_row])
                return
        try:
            data_to_write = []
            crawled_data = general.read_file(file_path)
            crawled_data = crawled_data.split("^!^!^")[:-1]
            for data in crawled_data:
                record_list = []
                temp_value_pair = data.split("|^|^|")[:-1]
                for single_pair in temp_value_pair:
                    record_list.append(single_pair.split("!:!:!")[1].replace("\u0000", ""))
                data_to_write.append(record_list)
            self.push_data2('found', data_to_write)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)
            self.push_data2("proxy_blocked", [[input_row[0], str(e)]])
            return


crawl = crawler()
crawl.start(crawl.initiate)
