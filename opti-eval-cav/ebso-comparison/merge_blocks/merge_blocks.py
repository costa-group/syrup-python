import csv
import re
import itertools 

fn_data_set = "/home/maria/opti/opti-eval/ebso-comparison/data/deduped_4bit_2500.csv"
data_set = list(csv.reader(open(fn_data_set)))

def get_source_bytecode(index):
    row = data_set[(index+1)] # ignore header
    source_program = row[0] 
    return source_program

def fix_block_and_part_id(row):
    path_name = row['block_id']
    # e.g. input_jsons/ethir_OK_block25472_blocks_block0.1_input.json
    numbers_in_path_name = re.findall(r'\d+', path_name)
    block_id = int(numbers_in_path_name[0])
    part_id = int(numbers_in_path_name[-1])
    row['block_id'] = block_id
    row['part_id'] = part_id

def add_source_bytecode(row):
    row['source bytecode'] = get_source_bytecode(row['block_id'])
    
def group_by_block_id(rows):
    key = lambda row : row['block_id']
    rows.sort(key=key)
    grpd = [[b for b in group] for _, group in itertools.groupby(rows, key=key)]
    return grpd

def combine(group):
    group.sort(key=lambda row : row['part_id'])
    combined = group[0]
    combined['part_id'] = 0
    
    target_gas_cost = 0
    shown_optimal = True
    no_model_found = False
    saved_gas = 0
    solver_time_in_sec = 0
    target_opcode = []
    target_disasm = []
    
    for d in group:
        tg2 = d['target_gas_cost']
        target_gas_cost = target_gas_cost + int(tg2) if tg2 else 0
        shown_optimal = shown_optimal and (d['shown_optimal'] == 'true')
        no_model_found = no_model_found or (d['no_model_found'] == 'true')
        saved_gas = saved_gas + int(d['saved_gas'])
        solver_time_in_sec = solver_time_in_sec + float(d['solver_time_in_sec'])
        target_opcode.append(d['target_opcode'])
        target_disasm.append(d['target_disasm'])
    
    combined['target_gas_cost'] = target_gas_cost + ((len(group)-1) * 20000)
    combined['shown_optimal'] = 'true' if shown_optimal else 'false'
    combined['no_model_found'] = 'true' if no_model_found else 'false'
    combined['saved_gas'] = saved_gas
    combined['solver_time_in_sec'] = solver_time_in_sec
    combined['target_opcode'] = "55".join(target_opcode)
    combined['target_disasm'] = " SSTORE ".join(target_disasm)

    return combined

def merge(fn_to_merge, fn_merged):

    original = list(csv.DictReader(open(fn_to_merge)))
    for row in original:
        # print("cleaning " + row["block_id"])
        fix_block_and_part_id(row)
        add_source_bytecode(row)
        
    print("Fixed block_id, added source_byte_code.")

    fieldnames = ['target_opcode', 'shown_optimal', 'no_model_found', 'block_id', 'target_disasm', 'source bytecode', 'solver_time_in_sec', 'part_id', 'saved_gas', 'target_gas_cost', 'source_gas_cost']
    fn = open(fn_merged, 'w')
    writer= csv.DictWriter(fn, fieldnames=fieldnames)

    writer.writeheader()
    for group in group_by_block_id(original) :
        print("processing block " + str(group[0]['block_id']))
        # combine if more than one are in the group
        if len(group) > 1:
            combined = combine(group)
            writer.writerow(combined)
        else :
            writer.writerow(group[0])

# print("give path to results from cluster")
#path_to_results_cluster = input()
path_to_results_cluster = "/home/maria/opti/opti-eval/ebso-comparison-new/results-syrup-cluster"           

#merge(path_to_results_cluster + "/results_Z3.csv", '../results-syrup-merged/results_Z3.csv')
#merge(path_to_results_cluster + "/results_BCLT.csv", '../results-syrup-merged/results_BCLT.csv')
merge(path_to_results_cluster + "/results_OMS.csv", '../results-syrup-merged/results_OMS.csv')
