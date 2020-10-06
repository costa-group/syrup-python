import subprocess
import csv

step = 0

def print_step():
    global step
    print("\nstep " + str(step), end = ": ")
    step = step+1

def query_csvsql(query, in_tables) :
    return subprocess.check_output(['csvsql'] + in_tables + ['--query', query, "-I", "--blanks"], encoding='UTF-8')
    
def read_csvsql(query, in_tables) :
    f = query_csvsql(query, in_tables).splitlines()
    rs = []
    for r in csv.DictReader(f, delimiter=',') :
        rs.append(r)
    return rs

print("-------------------------------------------------------------")
print("A Do-Nothing-Script for analyzing the solvers individually ")
print("-------------------------------------------------------------")

print_step()
print("give path to results_*.csv")
local_path_to_eval = input() # "/home/maria/opti/opti-eval/ebso-comparison/results-syrup-merged"

# to distinguish the keys for two different data sets
print_step()
print("Enter suffix for keys")
suffix = input()

def query_unique(clause):
    query = f"""
    SELECT solver, COUNT(*) AS count, SUM(saved_gas) AS saved_gas
    FROM results_PFT 
    WHERE {clause}
    GROUP BY solver"""
    result_lst = read_csvsql(query, [f'{local_path_to_eval}/results_PFT.csv'])
    r = {r['solver'] : r['count'] for r in result_lst}
    t = {r['solver'] : r['saved_gas'] for r in result_lst}
    return r, t 

aggregates = {
              'Unique' + suffix : 'unique_result = "true"',
              'UOPtim' + suffix : 'unique_shown_optimal = "true"',
              '+GSave' + suffix : 'saved_most_gas = "true"'}

r = {a : query_unique(aggregates[a])[0] for a in aggregates.keys()}
t = {a : query_unique(aggregates[a])[1] for a in aggregates.keys()}

tex = ""

def print_column(slvr) :
    return  " & \\num{" + r[a].get(slvr, '0') + "} " 

for a in aggregates.keys():
    tex += a + print_column('Z3') + print_column('BCLT') + print_column('OMS') + "\\\\ \n"

print(tex)
