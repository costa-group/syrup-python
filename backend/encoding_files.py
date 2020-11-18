import sys
import pathlib
import json

costabs_path = "/tmp/costabs/"
encoding_name = "encoding_Z3.smt2"

instr_map_file = "instruction.json"
opcode_map_file = "opcode.json"

encoding_stream = sys.stdout

def initialize_dir_and_streams(path_to_store):
    global encoding_stream
    global costabs_path

    # Files will be stored in costabs path, so we create it just in case
    # it doesn't exist.
    if path_to_store[-1] != "/":
        path_to_store += "/"

    costabs_path = path_to_store
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
