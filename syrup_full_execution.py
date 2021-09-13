#!/usr/bin/python3

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/ethir")
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/backend")
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/verification")
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/solution_generation")
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/params")
import glob
import argparse
from oyente_ethir import clean_dir, analyze_disasm_bytecode, analyze_bytecode, analyze_solidity, analyze_isolate_block, has_dependencies_installed
from syrup_optimization import get_sfs_dict
from python_syrup import execute_syrup_backend, execute_syrup_backend_combined
from disasm_generation import generate_disasm_sol
from sfs_verify import verify_sfs
import json
from solver_solution_verify import generate_solution_dict, check_solver_output_is_correct
from solver_output_generation import obtain_solver_output
import re
from paths import syrup_path, json_path, syrup_timeout, tmp_path, syrup_folder


def execute_ethir():
    global args
    
    if args.isolate_block:
        analyze_isolate_block(args_i = args)
        
    elif args.bytecode:
        analyze_bytecode(args_i = args)

    else:
        analyze_solidity(args_i = args)


def generate_files_for_solution(block_name, solver_output):
    generate_disasm_sol(block_name.split("_")[0], block_name, solver_output)


def check_log_information(files, log_dict):
    correct = True
    for file in files:
        block_name = file.split("/")[-1].rstrip(".json")
        try:
            execute_syrup_backend(args, file, log_dict[block_name])
        except KeyError:

            # Maybe block wasn't optimized, so we don't consider this case to be
            # an error per se.
            print("Log file does not contain info related to block " + block_name)
            continue

        solver_output = obtain_solver_output(block_name, args.solver, 1)
        if not check_solver_output_is_correct(solver_output):
            print("Failed to verify block " + block_name)
            correct = False

    if correct:
        print("All blocks have been verified correctly with the corresponding solver")


def new_check_log_information(files, log_dict, contract_name):
    correct = True
    execute_syrup_backend_combined(files, log_dict, contract_name, args.solver)
    solver_output = obtain_solver_output(contract_name, args.solver, 1)
    if not check_solver_output_is_correct(solver_output):
        print("Failed to verify block " + contract_name)
        correct = False

    if correct:
        print("All blocks have been verified correctly with the corresponding solver")



def main():
    global args

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-s",  "--source",    type=str, help="local source file name. Solidity by default. Use -b to process evm instead. Use stdin to read from stdin.")
    parser.add_argument( "-b",   "--bytecode",               help="read bytecode in source instead of solidity file", action="store_true")
    
    #Added by Pablo Gordillo
    parser.add_argument( "-e",   "--evm",                    help="Do not remove the .evm file.", action="store_true")
    #Added by Pablo Gordillo
    parser.add_argument( "-disasm", "--disassembly",        help="Consider a dissasembly evm file directly", action="store_true")
    parser.add_argument( "-in", "--init",        help="Consider the initialization of the fields", action="store_true")
    parser.add_argument( "-d", "--debug",                   help="Display the status of the stack after each opcode", action = "store_true")
    parser.add_argument( "-cfg", "--control-flow-graph",    help="Store the CFG", action="store_true")
    parser.add_argument( "-saco", "--saco",                 help="Translate EthIR RBR to SACO RBR", action="store_true")
    parser.add_argument( "-storage", "--storage",                 help="Split using SSTORE and MSTORE", action="store_true")
    #parser.add_argument("-ebso", "--ebso", help="Generate the info for EBSO in a json file", action = "store_true")
    parser.add_argument("-isb", "--isolate_block", help="Generate the RBR for an isolate block", action = "store_true")
    parser.add_argument("-solver", "--solver",             help="Choose the solver", choices = ["z3","barcelogic","oms"])
    parser.add_argument("-json", "--json",             help="The input file is a json that contains the SFS of the block to be analyzed", action="store_true")
    parser.add_argument("-v", "--verify",             help="Generate a verification report checking if the SFS of the original and the optimized block are the same", action="store_true")
    parser.add_argument("-optimize-run", "--optimize-run",             help="Enable optimization flag in solc compiler", action="store_true")
    parser.add_argument("-run", "--run",             help="Set for how many contract runs to optimize (200 by default if --optimize-run)", default=-1,action="store",type=int)
    parser.add_argument("-no-yul-opt", "--no-yul-opt",             help="Disable yul optimization in solc compiler (when possible)", action="store_true")
    parser.add_argument('-write-only', help="print smt constraint in SMT-LIB format,a mapping to instructions, and objectives", action='store_true')
    parser.add_argument('-at-most', help='add a constraint for each uninterpreted function so that they are used at most once',
                    action='store_true', dest='at_most')
    parser.add_argument('-pushed-once', help='add a constraint to indicate that each pushed value is pushed at least once',
                    action='store_true', dest='pushed_once')
    parser.add_argument("-tout", metavar='timeout', action='store', type=int, help="Timeout in seconds.")
    parser.add_argument("-inequality-gas-model", dest='inequality_gas_model', action='store_true',
                    help="Soft constraints with inequalities instead of equalities")
    parser.add_argument("-instruction-order", help='add a constraint representing the order among instructions',
                    action='store_true', dest='instruction_order')
    parser.add_argument("-no-output-before-pop", help='add a constraint representing the fact that the previous instruction'
                                                  'of a pop can only be a instruction that does not produce an element',
                    action='store_true', dest='no_output_before_pop')
    parser.add_argument("-initial-solution", dest='initial_solution', action='store_true',
                    help="Consider the instructions of blocks without optimizing as part of the encoding")
    parser.add_argument("-disable-default-encoding", dest='default_encoding', action='store_false',
                    help="Disable the constraints added for the default encoding")
    parser.add_argument("-number-instruction-gas-model", dest='number_instruction_gas_model', action='store_true',
                    help="Soft constraints for optimizing the number of instructions instead of gas")
    args = parser.parse_args()

    if not has_dependencies_installed():
        return

    if args.tout is not None:
        tout = args.tout
    else:
        tout = syrup_timeout

    clean_dir()
    
    if syrup_folder not in os.listdir(tmp_path):
        os.mkdir(syrup_path)

    
    os.mkdir(syrup_path+"solutions")

    if not args.json:
    
        execute_ethir()

        sfs_dict = get_sfs_dict()
        if args.solver:

            for f in glob.glob(json_path + "/*.json"):
                #run_command(syrup_bend_path + " " + f)
                execute_syrup_backend(args,f)
                
                if not args.write_only:

                    block_name = f.split("/")[-1].rstrip(".json")

                    solver_output = obtain_solver_output(block_name, args.solver, tout)
                    generate_files_for_solution(block_name, solver_output)

    else:

        with open(args.source) as f:
            sfs_dict = json.load(f)
        
        execute_syrup_backend(args)
        if not args.write_only:

            block_name = args.source.split("/")[-1].rstrip(".json")
            solver_output = obtain_solver_output(block_name, args.solver, tout)
            generate_files_for_solution(block_name, solver_output)

        if args.verify and not args.write_only:
            if verify_sfs(args.source, sfs_dict):
                print("Correct verification")
            else:
                print("SFS do not match")


if __name__=="__main__":
    main()
