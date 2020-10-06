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
    
solvers = ['Z3','BCLT','OMS','PFT']

results_tex = {}

print("give path to local evaluation folder")
local_path_to_eval = input()

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
                         'ebso': '3882',
                         'show_percent' : True},
    'optimized_optimal' : {'row_name': 'O',
                           'query': query_optimized_optimal,
                           'ebso': '393',
                           'show_percent' : True},
    'optimized_better' : {'row_name': 'B',
                          'query': query_optimized_better,
                          'ebso': '550',
                          'show_percent': True},
    'non_optimized' : {'row_name': 'N',
                       'query': query_non_optimized,
                       'ebso': 'n/a',
                       'show_percent': True},
    'total_gas_saved': {'row_name': 'G',
                        'query': query_total_gas_saved,
                        'ebso': '27726',
                        'show_percent': False},
    'no_model_found' : {'row_name': 'T',
                        'query': query_no_model_found,
                        'ebso': '56392',
                        'show_percent': True},
    'total_time' : {'row_name' : 'S',
                    'query': query_total_time,
                    'ebso': 'not avail.',
                    'show_percent': False}
}

table = collections.OrderedDict(table)

for key in table.keys():
    for solver in solvers:
        path_to_results = f'{local_path_to_eval}/results_{solver}.csv'
        table[key][solver] = read_csvsql(table[key]['query'](solver), [path_to_results])[0][key]
        
def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)
        
def show_percent(number):
    return "\SI{" + "{0:.2f}".format(num(number) / total_blocks * 100) + "}{\percent}"

total_blocks = 61217 # for ebso data set!

def show_solver_result(number, key):
    percent = "(" + show_percent(number) + ")" if table[key]['show_percent'] else ""
    return "\\num{" + number + "} " + percent

def show_ebso_result(key):
    result = table[key]['ebso']
    return show_solver_result(result, key) if result.isnumeric() else result
        
def show_row(key):
    columns_list = [table[key]['row_name']]
    columns_list.append(show_ebso_result(key))
    for solver in solvers:
        number = table[key][solver] 
        columns_list.append(show_solver_result(number, key))
    return (" & ".join(columns_list) + " \\\\")

# print table row for every key
for k in table.keys():
    print(show_row(k))

def show_newcommand_number(name, number):
    return "\\newcommand*{\\" + name + "}{\\num{" + number + "}\\xspace}"

def show_newcommand_percent(name, number):
    return "\\newcommand*{\\" + name + "}{" + show_percent(number) + "\\xspace}"

selected_solver = 'PFT'

print("")
print("")
print("% data set i Timeouts Ebso and All with Percentage")
print(show_newcommand_number("iTE", table['no_model_found']['ebso']))
print(show_newcommand_percent("iTEP", table['no_model_found']['ebso']))
print(show_newcommand_number("iTA", table['no_model_found'][selected_solver]))
print(show_newcommand_percent("iTAP", table['no_model_found'][selected_solver]))

print("% data set i Timeouts for MathSat")
print(show_newcommand_percent("iTMP", table['no_model_found']['OMS']))

print("")
print("% data set i Optimized optimal for Ebso and All")
print(show_newcommand_number("iOE", table['optimized_optimal']['ebso']))
print(show_newcommand_number("iOA", table['optimized_optimal'][selected_solver]))

print("")
print("% data set i Optimized Better All")
print(show_newcommand_percent("iBAP", table['optimized_better'][selected_solver]))

print("")
print("% data set i Already Optimized All")
print(show_newcommand_percent("iAAP", table['already_optimal'][selected_solver]))
print(show_newcommand_percent("iAMP",  table['already_optimal']['OMS']))

print("")
print("% data set i Optimized optimal and optimized Better MathSat")
print(show_newcommand_percent("iOBAP", int(table['optimized_optimal'][selected_solver]) + int(table['optimized_better'][selected_solver])))
print(show_newcommand_percent("iOBMP", int(table['optimized_optimal']['OMS']) + int(table['optimized_better']['OMS'])))

print("")
print("% total time in hours")
print("% data set i total of All in hours")
total_time_in_sec = num(table['total_time']['PFT'])
print("\\newcommand*{\\totalHours}{\\SI{" + str(math.ceil(total_time_in_sec/3600)) + "}{\hour}\\xspace}")
