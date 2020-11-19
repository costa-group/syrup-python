import sys
import pathlib
import json

costabs_path = "/tmp/costabs/"

encoding_name = "encoding_Z3.smt2"

instr_map_file = "instruction.json"
opcode_map_file = "opcode.json"

encoding_stream = sys.stdout

def initialize_dir_and_streams(path_to_store,solver,source_name = None):
    global encoding_stream
    global costabs_path

    # Files will be stored in costabs path, so we create it just in case
    # it doesn't exist.
    if path_to_store[-1] != "/":
        path_to_store += "/"

    if source_name:
        name = source.name.split("/")[-1].rstrip(".json")
        encoding_name = name+"_"+solver+".smt2"
        instr_map_file = name+"_"+instr_map_file
        opcode_map_file = name+"_"+opcode_map_file
        
    costabs_path = path_to_store+"/smt_encoding/"
    pathlib.Path(costabs_path).mkdir(parents=True, exist_ok=True)
    encoding_stream = open(costabs_path + encoding_name, 'w')

    
def write_encoding(string):
    print(string, file=encoding_stream)


def write_instruction_map(theta_instr):
    with open(costabs_path + instr_map_file, 'w') as f:
        f.write(json.dumps(theta_instr))


def write_opcode_map(instr_opcodes):
    with open(costabs_path + opcode_map_file, 'w') as f:
        f.write(json.dumps(instr_opcodes))
