#!/usr/bin/python3

from superoptimization_enconding import generate_smtlib_encoding
from utils import  add_bars_to_string
import json



if __name__ == "__main__":
    json_path = input()

    with open(json_path) as path:
        data = json.load(path)

    # Note that b0 can be either max_progr_len
    # or init_progr_len
    # b0 = data['max_progr_len']
    b0 = data['init_progr_len']

    bs = data['max_sk_sz']
    user_instr = data['user_instrs']
    initial_stack = list(map(add_bars_to_string, data['src_ws']))
    final_stack = list(map(add_bars_to_string, data['tgt_ws']))
    variables = list(map(add_bars_to_string, data['vars']))

    generate_smtlib_encoding(b0, bs, user_instr, variables, initial_stack, final_stack)
