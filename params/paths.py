import os

tmp_path = "/tmp/"
syrup_path = tmp_path + "syrup/"
json_path = syrup_path + "jsons"
smt_encoding_path = syrup_path +"smt_encoding/"
solutions_path = syrup_path +"solutions/"


project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

syrup_exec = project_path + "/syrup_full_execution.py"

z3_exec = project_path + "/bin/z3"

bclt_exec = project_path + "/bin/barcelogic"

oms_exec = project_path + "/bin/optimathsat"

csv_file = syrup_path + "solutions/statistics.csv"

syrup_timeout = 10