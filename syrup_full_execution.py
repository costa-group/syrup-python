#!/usr/bin/python3

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/ethir")
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/backend")
import glob
import shlex
import subprocess
import argparse
from oyente_ethir import clean_dir, analyze_disasm_bytecode, analyze_bytecode, analyze_solidity, analyze_isolate_block, has_dependencies_installed
from python_syrup import execute_syrup_backend

def init():
    global project_path
    project_path =  os.path.dirname(os.path.realpath(__file__))

    global ethir_syrup
    ethir_syrup = project_path + "/ethir"

    global z3_exec
    z3_exec = project_path + "/bin/z3"
    global bclt_exec
    bclt_exec = project_path + "/bin/barcelogic"
    global oms_exec
    oms_exec = project_path + "/bin/optimathsat"

    global disasm_generation_file
    disasm_generation_file = project_path + "/scripts/disasm_generation.py"
    global tmp_costabs
    tmp_costabs = "/tmp/costabs/"
    global json_dir
    json_dir = tmp_costabs + "jsons/"
    global sol_dir
    sol_dir = tmp_costabs + "sols/"

    global encoding_file
    encoding_file = tmp_costabs + "encoding_Z3.smt2"
    global result_file
    result_file = tmp_costabs + "solution.txt"
    global instruction_file
    instruction_file = tmp_costabs + "optimized_block_instructions.disasm_opt"

    print (sys.path)
    
def run_command(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                              stderr=FNULL)
    return solc_p.communicate()[0].decode()

def get_solver_to_execute(smt_file):

    if args.solver == "z3":
        return z3_exec + " -smt2 " + smt_file
    elif args.solver == "barcelogic":
        return bclt_exec
    else:
        return oms_exec


def main():

    global args
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-s",  "--source",    type=str, help="local source file name. Solidity by default. Use -b to process evm instead. Use stdin to read from stdin.")

    # parser.add_argument("--version", action="version", version="EthIR version 1.0.7 - Commonwealth")
    parser.add_argument( "-e",   "--evm",                    help="Do not remove the .evm file.", action="store_true")
    parser.add_argument( "-b",   "--bytecode",               help="read bytecode in source instead of solidity file", action="store_true")
    
    #Added by Pablo Gordillo
    parser.add_argument( "-disasm", "--disassembly",        help="Consider a dissasembly evm file directly", action="store_true")
    parser.add_argument( "-in", "--init",        help="Consider the initialization of the fields", action="store_true")
    parser.add_argument( "-d", "--debug",                   help="Display the status of the stack after each opcode", action = "store_true")
    parser.add_argument( "-cfg", "--control-flow-graph",    help="Store the CFG", action="store_true")
    parser.add_argument( "-saco", "--saco",                 help="Translate EthIR RBR to SACO RBR", action="store_true")
    #parser.add_argument("-ebso", "--ebso", help="Generate the info for EBSO in a json file", action = "store_true")
    parser.add_argument("-isb", "--isolate_block", help="Generate the RBR for an isolate block", action = "store_true")
    parser.add_argument( "-hashes", "--hashes",             help="Generate a file that contains the functions of the solidity file", action="store_true")
    parser.add_argument("-solver", "--solver",             help="Choose the solver", choices = ["z3","barcelogic","oms"])
    parser.add_argument("-json", "--json",             help="The input file is a json that contains the SFS of the block to be analyzed", choices = ["z3","barcelogic","oms"])
    parser.add_argument('-write-only', help="print smt constraint in SMT-LIB format,a mapping to instructions, and objectives", action='store_true')
    parser.add_argument('-at-most', help='add a constraint for each uninterpreted function so that they are used at most once',
                    action='store_true', dest='at_most')
    parser.add_argument('-pushed-once', help='add a constraint to indicate that each pushed value is pushed at least once',
                    action='store_true', dest='pushed_once')


    args = parser.parse_args()

    if not has_dependencies_installed():
        return


    init()    
    clean_dir()


    if not args.json:
    
        if args.isolate_block:
            analyze_isolate_block(args_i = args)

        elif args.bytecode:
            analyze_bytecode(args_i = args)

        else:
            analyze_solidity(args_i = args)


        if args.solver:
            for f in glob.glob(json_dir + "/*.json"):

                print (f)
                execute_syrup_backend(args,f)

                if not args.write_only:
                    exec_command = get_solver_to_execute(encoding_file)
                
                    solution = run_command(exec_command)
                    with open(result_file, 'w') as f:
                        f.write(solution)
                    run_command(disasm_generation_file)
                    run_command("mv " + instruction_file + " " + sol_dir + file.split('/')[-1].split('.')[0] + "_instructions.disasm-opt")
    else:
        pass
        #byP: Add to analyze only the sfs provided

if __name__=="__main__":
    main()
