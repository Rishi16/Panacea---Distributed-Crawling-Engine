from crawl.Backbone import essential

class log_Writer:
    log_file_path = ''
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
    def write(self, data):
        essential.write_file(self.log_file_path, str(data))