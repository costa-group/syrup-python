#!/usr/bin/python3

import glob
import os
import shlex
import subprocess


def init():

    project_path =  os.path.dirname(os.path.realpath(__file__))

    ethir_syrup = project_path + "ethir-syrup/"
    syrup_bend_path = project_path + "python-syrup-backend/python-syrup.py"
    
    z3_exec = project_path + "bin/z3"
    bclt_exec = project_path + "bin/barcelogic"
    oms_exec = project_path + "bin/optimathsat"


    disasm_generation_file = project_path + "scripts/disasm_generation.py"
    tmp_costabs = "/tmp/costabs/"
    json_dir = project_path + "jsons/"
    sol_dir = project_path + "sols/"
    
    encoding_file = tmp_costabs + "encoding_Z3.smt2"
    z3_result_file = tmp_costabs + "solution.txt"
    instruction_file = tmp_costabs + "optimized_block_instructions.disasm_opt"

    
def run_command(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                              stderr=FNULL)
    return solc_p.communicate()[0].decode()


if __name__=="__main__":

    init()
    
    for file in glob.glob(json_dir + "/*.json"):
        run_command(syrup_bend_path + " " + file)
        solution = run_command(z3_exec + " -smt2 " + encoding_file)
        with open(z3_result_file, 'w') as f:
            f.write(solution)
        run_command(disasm_generation_file)
        run_command("mv " + instruction_file + " " + sol_dir + file.split('/')[-1].split('.')[0] + "_instructions.disasm-opt")
