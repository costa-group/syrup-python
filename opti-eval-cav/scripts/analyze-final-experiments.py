import subprocess
import csv
import collections
import math

step = 0

def print_step():
    global step
    print("\nstep " + str(step), end = ": ")
    step = step+1

def query_csvsql(query, in_tables) :
    return subprocess.check_output(['csvsql'] + in_tables + ['--query', query], encoding='UTF-8')
    
def read_csvsql(query, in_tables) :
    f = query_csvsql(query, in_tables).splitlines()
    rs = []
    for r in csv.DictReader(f, delimiter=',') :
        rs.append(r)
    return rs
    
solvers = ['Z3','BCLT','OMS']
total_blocks = 46966 

def query_already_optimal(solver):
    return f"""SELECT COUNT(*) as already_optimal 
               FROM "results_{solver}" 
               WHERE shown_optimal AND saved_gas = 0"""

def query_optimized_optimal(solver):
    return f"""SELECT COUNT(*) as optimized_optimal
               FROM "results_{solver}" 
               WHERE saved_gas > 0 AND shown_optimal """

def query_optimized_better(solver):
    return f"""SELECT COUNT(*) as optimized_better 
    FROM "results_{solver}" 
    WHERE NOT no_model_found AND saved_gas > 0 AND NOT shown_optimal""" 

def query_non_optimized(solver):
    return f"""SELECT COUNT(*) as non_optimized 
               FROM "results_{solver}" 
               WHERE NOT no_model_found AND saved_gas = 0 AND NOT shown_optimal"""

def query_total_gas_saved(solver):
    return f"""SELECT CAST(SUM(saved_gas) AS INTEGER) as total_gas_saved 
               FROM 'results_{solver}'"""

def query_no_model_found(solver):
    return f"""SELECT COUNT(*) as no_model_found 
               FROM "results_{solver}" 
               WHERE no_model_found"""

def query_total_time(solver):
    return f"""SELECT ROUND(SUM(solver_time_in_sec), 2) as total_time 
               FROM 'results_{solver}'"""

table = {
    'already_optimal' : {'row_name': 'A',
                         'query': query_already_optimal,
                         'show_percent' : True},
    'optimized_optimal' : {'row_name': 'O',
                           'query': query_optimized_optimal,
                           'show_percent' : True},
    'optimized_better' : {'row_name': 'B',
                          'query': query_optimized_better,
                          'show_percent': True},
    'non_optimized' : {'row_name': 'N',
                       'query': query_non_optimized,
                       'show_percent': True},
    'no_model_found' : {'row_name': 'T',
                        'query': query_no_model_found,
                        'show_percent': True},
    'total_gas_saved': {'row_name': 'G',
                        'query': query_total_gas_saved,
                        'show_percent': False},
    'total_time' : {'row_name' : 'S',
                    'query': query_total_time,
                    'show_percent': False}
}

base_line = {
    'already_optimal' : {'Z3': 30854,
                         'BCLT': 30940,
                         'OMS': 31016,
                         'PFT': 31018},
    'optimized_optimal' : {'Z3': 12143,
                           'BCLT': 12311,
                           'OMS': 12536,
                           'PFT': 12546},
    'optimized_better' : {'Z3': 745,
                          'BCLT': 330,
                          'OMS': 638,
                          'PFT': 687},
    'non_optimized' : {'Z3': 1893,
                         'BCLT': 1340,
                         'OMS': 1507,
                         'PFT': 1680},
    'no_model_found' : { 'Z3': 1331,
                         'BCLT': 2045,
                         'OMS': 1269,
                         'PFT': 1035},
    'total_gas_saved': { 'Z3': 345267,
                         'BCLT': 327884,
                         'OMS': 354979,
                         'PFT': 358095},
    'total_time' : { 'Z3': 2603365.71,
                     'BCLT': 2378748.72,
                     'OMS': 2190273.38,
                     'PFT': 2076736.98}
}

improves_on = {
    'already_optimal' : 'increase',
    'optimized_optimal' : 'increase',
    'optimized_better' : 'increase',
    'non_optimized' : 'increase',
    'no_model_found' : 'decrease',
    'total_gas_saved': 'increase',
    'total_time' : 'decrease'
}

def show_percent(key, diff_percent, diff_number):
    color = 'red'
    if num(diff_percent) > 0 and improves_on[key] == 'increase' :
        color = 'green'
    if num(diff_percent) < 0 and improves_on[key] == 'decrease' :
        color = 'green'
    diff_number = "(" + str(diff_number) + ")" if key != 'total_gas_saved' and key != 'total_time' else ""
    arrow = " $\\uparrow$" if color == 'green' else " $\\downarrow$"
    sign = "+" if diff_percent > 0 else ""
    return "& {\color{" + color + "}" + sign + "\SI{" + "{0:.1f}".format(diff_percent) + "}{\percent}" + diff_number + arrow + "}"

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def show_neutral() :
    return "& {\color{gray} $\pm$ \SI{0}{\percent}}"

def show_diff(table, number, key, solver):
    diff_percent = (100 / base_line[key][solver] * num(number)) - 100
    diff_number = abs(base_line[key][solver] - num(number))
    if diff_number <= 5 or abs(diff_percent) < 0.1:
        return show_neutral()
    return show_percent(key, diff_percent, diff_number)
    
def show_solver_result(table, number, key, solver):
    return "\\num{" + number + "} " + show_diff(table, number, key, solver)

def show_row(table, key):
    columns_list = [table[key]['row_name']]
    for solver in solvers:
        number = table[key][solver] 
        columns_list.append(show_solver_result(table, number, key, solver))
    return (" & ".join(columns_list) + " \\\\")
    
results_tex = {}

cont = 'y'

paths = [
    '/home/maria/syrup-eval/experiments-final-version/program-length/scale-150',
    '/home/maria/syrup-eval/experiments-final-version/program-length/scale-200',
    '/home/maria/syrup-eval/experiments-final-version/stack-size/scale-150',
    '/home/maria/syrup-eval/experiments-final-version/stack-size/scale-200',
    '/home/maria/syrup-eval/experiments-final-version/redundant-clauses/at-most-once',
    '/home/maria/syrup-eval/experiments-final-version/redundant-clauses/at-least-once'
]

for local_path_to_eval in paths :
    
    print(f"compute {local_path_to_eval}")
    
    table = collections.OrderedDict(table)
    
    for key in table.keys():
        for solver in solvers:
            path_to_results = f'{local_path_to_eval}/results_{solver}.csv'
            table[key][solver] = read_csvsql(table[key]['query'](solver), [path_to_results])[0][key]

    # print table row for every key
    output_file = local_path_to_eval + '/experiments-final.tex'
    out = open(output_file, "w")
    for k in table.keys():
        out.write(show_row(table, k))
        out.write('\n')

    
