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

    # Timeout in s
    global tout
    tout = 30

    global oms_path
    oms_path = project_path + "/bin/optimathsat"

    global syrup_path
    syrup_path = project_path + "/backend/python_syrup.py"

    global syrup_flags
    syrup_flags = "-tout " + str(tout) + " -solver oms"

    global contracts_dir_path
    contracts_dir_path = project_path + "/examples/most_called"

    global sol_dir
    sol_dir = project_path + "/sols/"

    global disasm_generation_file
    disasm_generation_file = project_path + "/scripts/disasm_generation.py"
    # Timeout in seconds"

    global oms_flags
    oms_flags = "-stats"

    global solver_output_file
    solver_output_file = tmp_costabs + "/solution.txt"

    global encoding_file
    encoding_file = tmp_costabs + "/smt_encoding/encoding.smt2"

    global instruction_final_solution
    instruction_final_solution = tmp_costabs + "/optimized_block_instructions.disasm_opt"

    global results_dir
    results_dir = project_path + "/results/prueba/"


def run_command(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                              stderr=FNULL)
    return solc_p.communicate()[0].decode()


def analyze_file(solution):
    pattern = re.compile("\(gas (.*)\)")
    for match in re.finditer(pattern, solution):
        number = int(match.group(1))
        pattern2 = re.compile("range")
        if re.search(pattern2, solution):
            return number, False
        return number, True

if __name__=="__main__":
    init()
    pathlib.Path(tmp_costabs).mkdir(parents=True, exist_ok=True)
    pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True)
    for contract_path in [f.path for f in os.scandir(contracts_dir_path) if f.is_dir()]:
        rows_list = []
        for file in glob.glob(contract_path + "/*.json"):
            file_results = {}
            block_id = file.split('/')[-1]
            file_results['block_id'] = block_id
            with open(file) as path:
                data = json.load(path)
                source_gas_cost = data['current_cost']
                file_results['source_gas_cost'] = int(source_gas_cost)
            run_command(syrup_path + " " + file + " " + syrup_flags)
            solution = run_command(oms_path + " " + encoding_file + " " + oms_flags)
            tout_pattern = re.search(re.compile("not enabled"), solution)

            if tout_pattern:
                file_results['no_model_found'] = True
                file_results['shown_optimal'] = False
                file_results['solver_time_in_sec'] = tout
            else:

                file_results['no_model_found'] = False
                time_match = re.search(re.compile(":time-seconds\s*(\d+(\.\d*)?)"), solution)
                if time_match:
                    executed_time = float(time_match.group(1))
                    file_results['solver_time_in_sec'] = executed_time

                target_gas_cost, shown_optimal = analyze_file(solution)
                # Sometimes, solution reached is not good enough
                file_results['target_gas_cost'] = min(target_gas_cost, file_results['source_gas_cost'])
                file_results['shown_optimal'] = shown_optimal
                file_results['saved_gas'] = file_results['source_gas_cost'] - file_results['target_gas_cost']

                with open(solver_output_file, 'w') as f:
                    f.write(solution)

                run_command(disasm_generation_file)

                with open(instruction_final_solution, 'r') as f:
                    file_results['target_disasm'] = f.read()

            rows_list.append(file_results)

        df = pd.DataFrame(rows_list, columns=['block_id', 'target_gas_cost', 'shown_optimal', 'no_model_found',
                                          'source_gas_cost', 'saved_gas', 'solver_time_in_sec', 'target_disasm'])
        csv_file = results_dir + contract_path.split('/')[-1] + "_results_oms.csv"
        df.to_csv(csv_file)