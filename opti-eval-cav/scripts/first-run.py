from pathlib import Path
import os
import subprocess
import json
import time

def all_input_jsons(curr_dir):
    return Path(curr_dir).glob('../initial/ethir_OK/**/input.json')

def log_keys(path_to_json, keys):
    data = json.load(path_to_json.open())
    for key in keys:
        print("  " + key + ": " + str(data[key]))

def log_processing(path_to_json):
    block = "/".join(path_to_json.parts[-5:-1])
    print(time.asctime() + ": processing: " + block)
    
def log_input(path_to_json):
    print("Input:")
    log_keys(path_to_json, ['src_ws', 'tgt_ws'])
        
def log_result(path_to_json):
    print("Result:")
    log_keys(path_to_json, ['disasm', 'cost'])
    print("")

def del_output(path_to_input_json, file_names) :
    for file_name in file_names:
        try:
            path_to_input_json.with_name(file_name).unlink()
        except:
            pass
    
def call_opti(path_to_opti, path_to_input_json, solver, timeout):
    try:
        subprocess.run(
            [path_to_opti + str(solver) + ".sh", str(path_to_input_json), '-timeout', str(timeout)]
        )
        exit_code = 0
    except:
        exit_code = 2
        print("Error.")
    return exit_code

def run_examples(solvers, timeout):
    path_to_opti = '/home/maria/opti-src/run_'
    curr_dir = os.getcwd()
    
    print("Run examples with a timeout of " + str(timeout) + " seconds.\n")

    total = 0
    errored = 0

    for path_to_input_json in all_input_jsons(curr_dir) :
        log_processing(path_to_input_json)
        log_input(path_to_input_json)
        total = total + 1
        for solver in solvers :
            print("-------")
            print(solver)
            exit_code = call_opti(path_to_opti, path_to_input_json, solver, timeout)
            errored = errored + 1 if exit_code == 2 else errored

    print("Summary")
    print("-------")
    print("Total: " + str(total))
    print("Errors:" + str(errored))

    
def main():
    run_examples(["Z3", "BCLT", "OMS"], 10)
    
if __name__ == "__main__":
    main()
