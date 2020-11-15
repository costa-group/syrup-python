#!/usr/bin/python3
from typing import TextIO

from superoptimization_enconding import generate_smtlib_encoding
from utils import  add_bars_to_string
import json
import argparse
from encoding_files import initialize_dir_and_streams

costabs_path = "/tmp/costabs/"

def parse_data(json_path):
    with open(json_path) as path:
        data = json.load(path)

    # Note that b0 can be either max_progr_len
    # or init_progr_len
    # b0 = data['max_progr_len']
    b0 = data['init_progr_len']

    bs = data['max_sk_sz']
    user_instr = data['user_instrs']

    for instr in user_instr:
        instr['outpt_sk'] = list(map(add_bars_to_string, instr['outpt_sk']))
        instr['inpt_sk'] = list(map(add_bars_to_string, instr['inpt_sk']))

    initial_stack = list(map(add_bars_to_string, data['src_ws']))
    final_stack = list(map(add_bars_to_string, data['tgt_ws']))
    variables = list(map(add_bars_to_string, data['vars']))
    return b0, bs, user_instr, variables, initial_stack, final_stack



if __name__ == "__main__":
    ap = argparse.ArgumentParser(description='Backend of syrup tool')
    ap.add_argument('json_path', help='Path to json file that contains the SFS')
    ap.add_argument('-out', help='Path to dir where the smt is stored (by default, in ' + str(costabs_path) + ")",
                    nargs='?', default=costabs_path, metavar='dir')
    ap.add_argument('-write-only', help='print smt constraint in SMT-LIB format, '
                                                             'a mapping to instructions, and objectives',
                    action='store_true')

    args = vars(ap.parse_args())
    json_path = args['json_path']
    path = args['out']

    initialize_dir_and_streams(path)

    b0, bs, user_instr, variables, initial_stack, final_stack = parse_data(json_path)
    generate_smtlib_encoding(b0, bs, user_instr, variables, initial_stack, final_stack)
