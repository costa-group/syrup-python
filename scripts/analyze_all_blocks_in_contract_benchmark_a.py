#!/usr/bin/python3
import argparse
import os
import glob
import pathlib
import shlex
import subprocess
import re
import json
import pandas as pd
import sys
import resource
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/params")
from paths import project_path, oms_exec, syrup_exec, syrup_path, smt_encoding_path, json_path, z3_exec, bclt_exec
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/backend")
from encoding_utils import generate_phi_dict
from timeit import default_timer as timer
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/verification")
from sfs_verify import are_equals
from solver_solution_verify import generate_solution_dict, check_solver_output_is_correct
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/scripts")
import traceback


def modifiable_path_files_init():
    parser = argparse.ArgumentParser()

    parser.add_argument("-solver", "--solver", help="Choose the solver", choices=["z3", "barcelogic", "oms"],
                        required=True)
    parser.add_argument("-tout", metavar='timeout', action='store', type=int, help="timeout in seconds", required=True)
    parser.add_argument("-syrup-encoding-flags", metavar='syrup_flags', action='store', type=str,
                        help="flags to select the desired Max-SMT encoding. "
                             "Use same format as the one in syrup_full_execution. "
                             "First argument must be preceded by a blank space", required=True)
    parser.add_argument("-csv-folder", metavar='csv_folder', action='store', type=str,
                        help="folder that will store the csvs containing the statistics per file. Inside that folder, "
                             "another subfolder is created: solver_name + _ + timeout + 's'", required=True)

    args = parser.parse_args()

    # Selected solver. Only three possible values:
    # "oms", "z3", "barcelogic"
    global solver
    solver = args.solver

    # Timeout in s
    global tout
    tout = args.tout

    # Folder in which the csvs are stored. A csv is generated per each analyzed file
    global results_dir
    results_dir = args.csv_folder
    if results_dir[-1] != "/":
        results_dir += "/"

    results_dir += solver + "_" + str(tout) + "s/"

    # Flags activated for the syrup backend (i.e. the Max-SMT encoding).
    # Do not include timeout flag nor solver flag, only for encoding flags
    global syrup_encoding_flags
    syrup_encoding_flags = args.syrup_encoding_flags


def not_modifiable_path_files_init():
    global contracts_dir_path
    contracts_dir_path = project_path + "/results-a/SFS_OK"

    global disasm_generation_file
    disasm_generation_file = project_path + "solution_generation/disasm_generation.py"

    global oms_flags
    oms_flags = " "

    global syrup_backend_exec
    syrup_backend_exec = project_path + "backend/python_syrup.py"

    global solver_output_file
    solver_output_file = syrup_path + "solution.txt"

    global encoding_file
    encoding_file = smt_encoding_path + "encoding.smt2"

    global instruction_final_solution
    instruction_final_solution = syrup_path + "optimized_block_instructions.disasm_opt"

    global gas_final_solution
    gas_final_solution = syrup_path + "gas.txt"

    global final_json_path
    final_json_path = json_path + "block__block0_input.json"

    global final_disasm_blk_path
    final_disasm_blk_path = syrup_path + "block.disasm_blk"

    global syrup_full_execution_flags
    syrup_full_execution_flags = " -isb -storage -s " + final_disasm_blk_path

    global log_path
    log_path = project_path + "logs"

    global log_file
    log_file = log_path + "log_oms.log"

    global block_log
    block_log = syrup_path + "block.log"

    global syrup_encoding_flags
    global tout
    global solver
    global syrup_flags
    syrup_flags = " " + syrup_encoding_flags + " -tout " + str(tout) + " -solver " + solver


def init():
    modifiable_path_files_init()
    not_modifiable_path_files_init()


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


def analyze_file_oms(solution):
    pattern = re.compile("\(gas (.*)\)")
    for match in re.finditer(pattern, solution):
        number = int(match.group(1))
        pattern2 = re.compile("range")
        if re.search(pattern2, solution):
            return number, False
        return number, True


def submatch_z3(string):
    subpattern = re.compile("\(interval (.*) (.*)\)")
    for submatch in re.finditer(subpattern, string):
        return int(submatch.group(2))
    return -1


def analyze_file_z3(solution):
    pattern = re.compile("\(gas (.*)\)")
    for match in re.finditer(pattern, solution):
        number = submatch_z3(match.group(1))
        if number == -1:
            return int(match.group(1)), True
        else:
            return number, False


def submatch_barcelogic(string):
    subpattern = re.compile("\(cost (.*)\)")
    for submatch in re.finditer(subpattern, string):
        return int(submatch.group(1))
    return -1


def analyze_file_barcelogic(solution):
    pattern = re.compile("\(optimal (.*)\)")
    for match in re.finditer(pattern, solution):
        return int(match.group(1)), True
    return submatch_barcelogic(solution), False


def analyze_file(solution):
    global solver
    if solver == "oms":
        return analyze_file_oms(solution)
    elif solver == "z3":
        return analyze_file_z3(solution)
    else:
        return analyze_file_barcelogic(solution)


def get_solver_to_execute():
    global encoding_file
    global tout

    if solver == "z3":
        return z3_exec + " -smt2 " + encoding_file
    elif solver == "barcelogic":
        if tout is None:
            return bclt_exec + " -file " + encoding_file
        else:
            return bclt_exec + " -file " + encoding_file + " -tlimit " + str(tout)
    else:
        return oms_exec + " " + encoding_file


def get_tout_found_per_solver(solution):
    global solver
    if solver == "z3":
        return re.search(re.compile("model is not"), solution)
    elif solver == "barcelogic":
        target_gas_cost, _ = analyze_file_barcelogic(solution)
        return target_gas_cost == -1
    else:
        return re.search(re.compile("not enabled"), solution)


if __name__=="__main__":
    init()
    pathlib.Path(syrup_path).mkdir(parents=True, exist_ok=True)
    pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)

    # file_to_rem = pathlib.Path(log_file)
    # file_to_rem.unlink(missing_ok=True)

    already_analyzed_contracts = glob.glob(results_dir + "/*.csv")

    log_size_in_bytes = []

    for contract_path in [f.path for f in os.scandir(contracts_dir_path) if f.is_dir()]:
        rows_list = []
        log_dict = dict()
        csv_file = results_dir + contract_path.split('/')[-1] + "_results_" + solver + ".csv"

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
            run_command(syrup_backend_exec + " " + file + " " + syrup_flags)
            smt_exec_command = get_solver_to_execute()
            solution, executed_time = run_and_measure_command(smt_exec_command)
            executed_time = round(executed_time, 3)
            tout_pattern = get_tout_found_per_solver(solution)

            if tout_pattern:
                file_results['no_model_found'] = True
                file_results['shown_optimal'] = False
                file_results['solver_time_in_sec'] = executed_time
            else:
                # Checks solver log is correct
                log_info = generate_solution_dict(solution)
                log_dict[block_id] = log_info
                with open(block_log, 'w') as path:
                    json.dump(log_info, path)
                os.remove(encoding_file)
                run_command(syrup_backend_exec + " " + file + " -check-log-file " + block_log)
                solver_output, verifier_time = run_and_measure_command(oms_exec + " " + encoding_file)
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
                    # It cannot be negative
                    file_results['saved_gas'] = max(0, file_results['source_gas_cost'] - int(file_results['real_gas']))

                try:

                    run_command(syrup_exec + " " + syrup_full_execution_flags)

                    with open(final_json_path) as path:
                        data2 = json.load(path)
                        start = timer()
                        file_results['result_is_correct'] = are_equals(data, data2)
                        end = timer()
                        file_results['verifier_time'] = end-start
                except Exception:

                    with open(log_file, "a+") as f:
                        error_message = traceback.format_exc()
                        print("File " + file, file=f)
                        print("Error message: " + error_message, file=f)
                        print("\n\n", file=f)
                    continue

            rows_list.append(file_results)

        contract_results = dict()
        contract_results['contract_id'] = contract_path.split('/')[-1]
        log_file = syrup_path + "/" + contract_path.split('/')[-1] + ".json"
        with open(log_file, "w") as log_f:
            json.dump(log_dict, log_f)
        contract_results['log_size'] = os.path.getsize(log_file)
        log_size_in_bytes.append(contract_results)
        df = pd.DataFrame(rows_list, columns=['block_id', 'target_gas_cost', 'real_gas',
                                              'shown_optimal', 'no_model_found', 'source_gas_cost', 'saved_gas',
                                              'solver_time_in_sec', 'target_disasm', 'init_progr_len',
                                              'final_progr_len',
                                              'number_of_necessary_uninterpreted_instructions',
                                              'number_of_necessary_push', 'result_is_correct', 'verifier_time',
                                              'solution_checked_by_solver', 'time_verify_solution_solver'])
        df.to_csv(csv_file)

    final_df = pd.DataFrame(log_size_in_bytes, columns=['contract_id', 'log_size'])
    pathlib.Path(project_path+"/log_csv/").mkdir(parents=True, exist_ok=True)
    final_df.to_csv(project_path+"/log_csv/log_size.csv")