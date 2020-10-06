import csv
import itertools

step = 0

def print_step():
    global step
    print("\nstep " + str(step), end = ": ")
    step = step+1

print("-------------------------------------------------------------")
print("A Do-Nothing-Script for computing the protfolio result ")
print("-------------------------------------------------------------")

print_step()
print("give path to results_*.csv")
path_to_results = input()

def read_and_sort(fn) :
    results = list(csv.DictReader(open(fn)))
    results.sort(key=lambda row : row['block_id'])
    return results

def process_row(r1, r2):
    if r1['saved_gas'] > r2['saved_gas']:
        return r1, r2
    elif r1['saved_gas'] < r2['saved_gas']:
        return r2, r1
    else: # equal gas savedg
        if r1['shown_optimal'] == 'true' and r2['shown_optimal'] == 'false':
            return r1, r2 
        elif r2['shown_optimal'] == 'true' and r1['shown_optimal'] == 'false':
            return r2, r1
        else: # neither or both optimal
            if r1['no_model_found'] == 'false' and r2['no_model_found'] == 'true':
                return r1, r2
            elif r1['no_model_found'] == 'true' and r2['no_model_found'] == 'false':
                return r2, r1
            else: # neither or both found a model
                if r1['solver_time_in_sec'] < r2['solver_time_in_sec']:
                    return r1, r2
                else:
                    return r2, r1
    
results_Z3 = read_and_sort(f'{path_to_results}/results_Z3.csv')
results_BCLT = read_and_sort(f'{path_to_results}/results_BCLT.csv')
results_OMS = read_and_sort(f'{path_to_results}/results_OMS.csv')

fieldnames_ebso = ['target_opcode', 'shown_optimal', 'no_model_found', 'block_id', 'target_disasm', 'source bytecode', 'solver_time_in_sec', 'part_id', 'saved_gas', 'target_gas_cost', 'source_gas_cost', 'solver', 'unique_result', 'saved_most_gas', 'unique_shown_optimal']

fieldnames = ['target_opcode', 'shown_optimal', 'no_model_found', 'block_id', 'target_disasm', 'solver_time_in_sec', 'part_id', 'saved_gas', 'target_gas_cost', 'source_gas_cost', 'solver', 'unique_result', 'saved_most_gas', 'unique_shown_optimal']

fn = open(f'{path_to_results}/results_PFT.csv', 'w')
writer= csv.DictWriter(fn, fieldnames=fieldnames_ebso)

writer.writeheader()

def cast_values(r):
    r['saved_gas'] = int(r['saved_gas'])
    r['solver_time_in_sec'] = float(r['solver_time_in_sec'])

for r_Z3,r_BCLT,r_OMS in zip(results_Z3,results_BCLT,results_OMS):
    r_Z3['solver'] = 'Z3'
    r_BCLT['solver'] = 'BCLT'
    r_OMS['solver'] = 'OMS'

    cast_values(r_Z3)
    cast_values(r_BCLT)
    cast_values(r_OMS)
    
    winner,loser1 = process_row(r_Z3, r_BCLT)
    winner,loser2 = process_row(winner, r_OMS)
    
    winner['unique_result'] = 'true' if winner['no_model_found'] == 'false' \
        and loser1['no_model_found'] == 'true'\
        and loser2['no_model_found'] == 'true' else 'false'

    winner['saved_most_gas'] = 'true' if winner['saved_gas'] > loser1['saved_gas'] \
      and winner['saved_gas'] > loser2['saved_gas'] else 'false'
 
    winner['unique_shown_optimal'] = 'true' if winner['shown_optimal'] == 'true'\
        and loser1['shown_optimal'] == 'false' \
        and loser2['shown_optimal'] == 'false' else 'false'
    
    writer.writerow(winner)
