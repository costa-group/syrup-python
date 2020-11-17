#!/usr/bin/python3

import glob
import os
import pathlib
import shlex
import subprocess
import re
import json
import math

project_path = "/home/alejandro/repos/syrup-python/"
tmp_costabs = "/tmp/costabs/"

z3_path = project_path + "bin/z3"
syrup_path = project_path + "python-syrup-backend/python-syrup.py"
syrup_flags = " "
json_dir = project_path + "jsons/"
sol_dir = project_path + "sols/"
# Timeout in seconds
tout = 180
z3_flags = " -st -T:" + str(tout)

solution_log = tmp_costabs + "times.log"
times_json = tmp_costabs + "times.json"
encoding_file = tmp_costabs + "encoding_Z3.smt2"

def run_command(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                              stderr=FNULL)
    return solc_p.communicate()[0].decode()


if __name__=="__main__":
    solution_times = []
    file_results = {}
    pathlib.Path(tmp_costabs).mkdir(parents=True, exist_ok=True)

    with open(solution_log, 'w') as f:
        for file in glob.glob(json_dir + "/*.json"):
            run_command(syrup_path + " " + file + " " + syrup_flags)
            solution = run_command(z3_path + " -smt2 " + encoding_file + " " + z3_flags)
            tout_pattern = re.search(re.compile("timeout"), solution)
            f.write("Analyzing file " + file.split('/')[-1])
            if tout_pattern:
                print(": Timeout", file=f)
                solution_times.append(-1)
                file_results[file.split('/')[-1]] = math.inf
            else:
                time_match = re.search(re.compile(":total-time\s*(\d+(\.\d*)?)"), solution)
                if time_match:
                    executed_time = float(time_match.group(1))
                    print(": Execution time " + str(executed_time) + " s", file=f)
                    solution_times.append(executed_time)
                    file_results[file.split('/')[-1]] = executed_time
                else:
                    file_results[file.split('/')[-1]] = math.inf
    number_of_analyzed_contracts = len(solution_times)
    solution_times = list(filter(lambda x: x >= 0, solution_times))
    number_of_finished_contracts = len(solution_times)

    sol_json = {'total_contracts' : number_of_analyzed_contracts,
                'non_timeout_total_contracts' : number_of_finished_contracts,
                'times' : sorted(solution_times) , 'times_per_file' :  file_results}

    with open(times_json, 'w') as f:
        f.write(json.dumps(sol_json))
