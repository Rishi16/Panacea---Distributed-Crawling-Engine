# class abc:
#     status = ''
#     def __init__(self):
#         self.status = 1
#
# class xyz:
#     def __init__(self, bb):
#         self.abc_in = bb
#     def print_val(self):
#         print(self.abc_in.status)
#
#
# bb = abc()
# aa = xyz(bb)
# abc.status = 5
# aa.print_val()

# import status
#
# status.init()
# print(status.current_path)
from batch import  Batch
import essential
import status
server_details_path = 'E:\\Harsh\\python_projects\\panacea\\Team_data\\Lazada_product_matching\\Servers\\farnell.pbf'
server_details = essential.file_to_list(server_details_path)
team_name_for_batch = 'Lazada_product_matching'
batch_name_local = 'Farnell_US_prod'
status.current_path = 'E:\\Harsh\\python_projects\\panacea'
status.batch_in_system[team_name_for_batch] = [batch_name_local]
status.batch_status[team_name_for_batch] = {batch_name_local: 'running'}
Batch.generate_report(server_details, team_name_for_batch, batch_name_local)
# Batch.clean_batch_process(server_details, team_name_for_batch, batch_name_local)