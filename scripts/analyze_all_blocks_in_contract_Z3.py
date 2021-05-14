#!/usr/bin/python3
import os
import glob
import pathlib
import shlex
import subprocess
import re
import json
import traceback

import pandas as pd
import sys
import resource
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/backend")
from encoding_utils import generate_phi_dict
from timeit import default_timer as timer
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/verification")
from sfs_verify import are_equals
from solver_solution_verify import generate_solution_dict, check_solver_output_is_correct
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/scripts")


def init():
    global project_path
    project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    global tmp_costabs
    tmp_costabs = "/tmp/costabs"

    # Timeout in s
    global tout
    tout = 1

    global z3_path
    z3_path = project_path + "/bin/z3"

    global syrup_path
    syrup_path = project_path + "/backend/python_syrup.py"

    global syrup_flags
    syrup_flags = "-tout " + str(tout) + " -solver z3"

    global contracts_dir_path
    contracts_dir_path = project_path + "/examples/most_called"

    global sol_dir
    sol_dir = project_path + "/sols/"

    global disasm_generation_file
    disasm_generation_file = project_path + "/scripts/disasm_generation.py"
    # Timeout in seconds

    global z3_flags
    z3_flags = " "

    global solver_output_file
    solver_output_file = tmp_costabs + "/solution.txt"

    global encoding_file
    encoding_file = tmp_costabs + "/smt_encoding/encoding.smt2"

    global instruction_final_solution
    instruction_final_solution = tmp_costabs + "/optimized_block_instructions.disasm_opt"

    global gas_final_solution
    gas_final_solution = tmp_costabs + "/gas.txt"

    global results_dir
    results_dir = project_path + "/results/prueba/z3_" + str(tout) + "s/"

    global syrup_full_execution_path
    syrup_full_execution_path = project_path + "/syrup_full_execution.py"

    global final_json_path
    final_json_path = tmp_costabs + "/jsons/block__block0_input.json"

    global final_disasm_blk_path
    final_disasm_blk_path = tmp_costabs + "/block.disasm_blk"

    global syrup_full_execution_flags
    syrup_full_execution_flags = " -isb -storage -s " + final_disasm_blk_path

    global log_path
    log_path = project_path + "/logs"

    global log_file
    log_file = log_path + "/log_Z3.log"

    global block_log
    block_log = tmp_costabs + "/block.log"


def run_command(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                              stderr=FNULL)
    return solc_p.communicate()[0].decode()


def run_and_measure_command(cmd):
    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    solution = run_command(cmd)
    usage_stop = resource.getrusage(resource.RUSAGE_CHILDREN)
    return solution, usage_stop.ru_utime + usage_stop.ru_stime - usage_start.ru_utime - usage_start.ru_stime


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
    pathlib.Path(tmp_costabs).mkdir(parents=True, exist_ok=True)
    pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)

    file_to_rem = pathlib.Path(log_file)
    file_to_rem.unlink(missing_ok=True)

    already_analyzed_contracts = glob.glob(results_dir + "/*.csv")

    for contract_path in [f.path for f in os.scandir(contracts_dir_path) if f.is_dir()]:
        rows_list = []
        csv_file = results_dir + contract_path.split('/')[-1] + "_results_z3.csv"

        if csv_file in already_analyzed_contracts:
            continue

        for file in glob.glob(contract_path + "/*.json"):
            file_results = {}
            block_id = file.split('/')[-1].rstrip(".json")
            file_results['block_id'] = block_id
            with open(file) as path:
                data = json.load(path)
                source_gas_cost = data['current_cost']
                file_results['source_gas_cost'] = int(source_gas_cost)
                init_program_length = data['init_progr_len']
                file_results['init_progr_len'] = int(init_program_length)
                user_instr = data['user_instrs']
                final_stack = data['tgt_ws']
                file_results['number_of_necessary_uninterpreted_instructions'] = len(user_instr)
                file_results['number_of_necessary_push'] = len(generate_phi_dict(user_instr, final_stack))
                initial_stack = data['src_ws']
            run_command(syrup_path + " " + file + " " + syrup_flags)
            solution, executed_time = run_and_measure_command(z3_path + " -smt2 " + encoding_file + " " + z3_flags)
            executed_time = round(executed_time, 3)
            tout_pattern = re.search(re.compile("model is not"), solution)

            if tout_pattern:
                file_results['no_model_found'] = True
                file_results['shown_optimal'] = False
                file_results['solver_time_in_sec'] = executed_time
            else:
                # Checks solver log is correct
                log_info = generate_solution_dict(solution)
                with open(block_log, 'w') as path:
                    json.dump(log_info, path)
                os.remove(encoding_file)
                run_command(syrup_path + " " + file + " -check-log-file " + block_log + " -solver z3")
                solver_output, verifier_time = run_and_measure_command(z3_path + " " + encoding_file)
                verifier_time = round(verifier_time, 3)
                file_results['solution_checked_by_solver'] = check_solver_output_is_correct(solver_output)
                file_results['time_verify_solution_solver'] = verifier_time
                file_results['no_model_found'] = False
                file_results['solver_time_in_sec'] = executed_time

                target_gas_cost, shown_optimal = analyze_file(solution)
                # Sometimes, solution reached is not good enough
                file_results['target_gas_cost'] = min(target_gas_cost, file_results['source_gas_cost'])
                file_results['shown_optimal'] = shown_optimal

                with open(solver_output_file, 'w') as f:
                    f.write(solution)

                run_command(disasm_generation_file)

                with open(instruction_final_solution, 'r') as f:
                    instructions_disasm = f.read()
                    file_results['target_disasm'] = instructions_disasm
                    # Check all those strings that are not numbers
                    number_of_instructions = len(list(filter(lambda elem: not elem.isnumeric() and elem != '',
                                                             instructions_disasm.split(' '))))
                    file_results['final_progr_len'] = number_of_instructions

                    # Generate the disasm_blk file, including the size of the initial stack in the first
                    # line and the disasm instructions in the second one. This will be used to check if the
                    # initial SFS and the new generated one are equivalent
                    with open(final_disasm_blk_path, 'w') as f2:
                        print(len(initial_stack), file=f2)
                        print(instructions_disasm, file=f2)

                with open(gas_final_solution, 'r') as f:
                    file_results['real_gas'] = f.read()
                    file_results['saved_gas'] = file_results['source_gas_cost'] - int(file_results['real_gas'])
                try:

                    run_command(syrup_full_execution_path + " " + syrup_full_execution_flags)

                    with open(final_json_path) as path:
                        data2 = json.load(path)
                        start = timer()
                        file_results['result_is_correct'] = are_equals(data, data2)
                        end = timer()
                        file_results['verifier_time'] = end - start

                except Exception:

                    with open(log_file, "a+") as f:
                        error_message = traceback.format_exc()
                        print("File " + file, file=f)
                        print("Error message: " + error_message, file=f)
                        print("\n\n", file=f)
                    continue

            rows_list.append(file_results)

        df = pd.DataFrame(rows_list, columns=['block_id', 'target_gas_cost', 'real_gas',
                                              'shown_optimal', 'no_model_found', 'source_gas_cost', 'saved_gas',
                                              'solver_time_in_sec', 'target_disasm', 'init_progr_len',
                                              'final_progr_len',
                                              'number_of_necessary_uninterpreted_instructions',
                                              'number_of_necessary_push', 'result_is_correct', 'verifier_time',
                                              'solution_checked_by_solver', 'time_verify_solution_solver'])
        df.to_csv(csv_file)
