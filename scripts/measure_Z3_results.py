#!/usr/bin/python3
import os
import glob
import pathlib
import shlex
import subprocess
import re
import json
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/scripts")


def init():
    global project_path
    project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    global tmp_costabs
    tmp_costabs = "/tmp/costabs"

    global z3_path
    z3_path = project_path + "/bin/z3"

    global syrup_path
    syrup_path = project_path + "/backend/python_syrup.py"

    global syrup_flags
    syrup_flags = " "

    global json_dir
    json_dir = project_path + "/jsons/"

    global sol_dir
    sol_dir = project_path + "/sols/"

    global disasm_generation_file
    disasm_generation_file = project_path + "/scripts/disasm_generation.py"
    # Timeout in seconds

    global tout
    tout = 180

    global z3_flags
    z3_flags = " -st -T:" + str(tout)

    global z3_result_file
    z3_result_file = tmp_costabs + "/solution.txt"

    global solution_log
    solution_log = tmp_costabs + "/times.log"

    global times_json
    times_json = tmp_costabs + "/times.json"

    global encoding_file
    encoding_file = tmp_costabs + "/smt_encoding/encoding_Z3.smt2"

    global instruction_final_solution
    instruction_final_solution = tmp_costabs + "/optimized_block_instructions.disasm_opt"

    global csv_path
    csv_path = tmp_costabs + "/results_Z3.csv"


def run_command(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                              stderr=FNULL)
    return solc_p.communicate()[0].decode()


def submatch(string):
    subpattern = re.compile("\(interval (.*) (.*)\)")
    for submatch in re.finditer(subpattern, string):
        return int(submatch.group(2))
    return -1


def analyze_file(solution):
    pattern = re.compile("\(gas (.*)\)")
    for match in re.finditer(pattern, solution):
        number = submatch(match.group(1))
        if number == -1:
            return int(match.group(1)), True
        else:
            return number, False


if __name__=="__main__":
    init()
    rows_list = []
    pathlib.Path(tmp_costabs).mkdir(parents=True, exist_ok=True)
    for file in glob.glob(json_dir + "/*.json"):
        file_results = {}
        block_id = file.split('/')[-1]
        file_results['block_id'] = block_id
        with open(file) as path:
            data = json.load(path)
            source_gas_cost = data['current_cost']
            file_results['source_gas_cost'] = int(source_gas_cost)
        run_command(syrup_path + " " + file + " " + syrup_flags)
        solution = run_command(z3_path + " -smt2 " + encoding_file + " " + z3_flags)
        tout_pattern = re.search(re.compile("timeout"), solution)

        if tout_pattern:
            file_results['no_model_found'] = True
            file_results['shown_optimal'] = False
            file_results['solver_time_in_sec'] = tout
        else:

            file_results['no_model_found'] = False
            time_match = re.search(re.compile(":total-time\s*(\d+(\.\d*)?)"), solution)
            if time_match:
                executed_time = float(time_match.group(1))
                file_results['solver_time_in_sec'] = executed_time

            target_gas_cost, shown_optimal = analyze_file(solution)
            file_results['target_gas_cost'] = target_gas_cost
            file_results['shown_optimal'] = shown_optimal
            file_results['saved_gas'] = file_results['source_gas_cost'] - file_results['target_gas_cost']

            with open(z3_result_file, 'w') as f:
                f.write(solution)

            run_command(disasm_generation_file)

            with open(instruction_final_solution, 'r') as f:
                file_results['target_disasm'] = f.read()

        rows_list.append(file_results)

    df = pd.DataFrame(rows_list, columns=['block_id', 'target_gas_cost', 'shown_optimal', 'no_model_found',
                                          'source_gas_cost', 'saved_gas', 'solver_time_in_sec', 'target_disasm'])
    df.to_csv(csv_path)