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
    
results_tex = {}

solver = "PFT"

path_to_ebso = '../results-ebso/result.csv'
path_to_syrup = f'../results-syrup-merged/results_{solver}.csv'

# syrups saves as much as ebso => semtanics not helping
query_both_optimized_optimal = f"""  
SELECT COUNT(*) as both_optimized_optimal, SUM(syrup.'saved_gas') AS gas_syrup, SUM(ebso.'gas saved') AS gas_ebso
FROM 'results_{solver}' AS syrup JOIN 'result' AS ebso
ON ebso.'source bytecode' = syrup.'source bytecode'
WHERE ebso.'translation validation' = 'true' AND ebso.'gas saved' > 0 AND ebso.'known optimal' = 'true' AND ebso.'gas saved' = syrup.saved_gas
"""
both_optimized_optimal = read_csvsql(query_both_optimized_optimal, [path_to_ebso, path_to_syrup])[0]

# syrup saves less gas, but claims optimiality => impact of semantics
query_benefit_of_semantics = f"""  
SELECT COUNT(*) as benefit_of_semantics, SUM(syrup.'saved_gas') AS gas_syrup, SUM(ebso.'gas saved') AS gas_ebso
FROM 'results_{solver}' AS syrup JOIN 'result' AS ebso
ON ebso.'source bytecode' = syrup.'source bytecode'
WHERE ebso.'translation validation' = 'true' AND ebso.'gas saved' > 0 AND ebso.'gas saved' > syrup.saved_gas AND syrup.'shown_optimal' = 'true'
"""

benefit_of_semantics = read_csvsql(query_benefit_of_semantics, [path_to_ebso, path_to_syrup])[0]

# syrup saves more gas than ebso (not because of timeout)
query_syrup_optimizes_more = f"""
SELECT COUNT(*) as syrup_optimizes_more, SUM(syrup.'saved_gas') AS gas_syrup, SUM(ebso.'gas saved') AS gas_ebso
FROM 'results_{solver}' AS syrup JOIN 'result' AS ebso
ON ebso.'source bytecode' = syrup.'source bytecode'
WHERE ebso.'translation validation' = 'true' AND ebso.'gas saved' > 0 AND ebso.'gas saved' < syrup.saved_gas 
"""

syrup_optimizes_more = read_csvsql(query_syrup_optimizes_more, [path_to_ebso, path_to_syrup])[0]

tex = ""
tex += "\\newcommand*{\\bothOptimizedOptimal}{\\num{" + both_optimized_optimal['both_optimized_optimal'] +"}\\xspace} \n"
tex += "\\newcommand*{\\bothOptimizedOptimalSyrup}{\\num{" + both_optimized_optimal['gas_syrup'] +"}\\xspace} \n"
tex += "\\newcommand*{\\bothOptimizedOptimalEbso}{\\num{" + both_optimized_optimal['gas_ebso'] +"}\\xspace} \n"

tex += "\\newcommand*{\\benefitOfSemantics}{\\num{" + benefit_of_semantics['benefit_of_semantics'] +"}\\xspace} \n"
tex += "\\newcommand*{\\benefitOfSemanticsSyrup}{\\num{" + benefit_of_semantics['gas_syrup'] +"}\\xspace} \n"
tex += "\\newcommand*{\\benefitOfSemanticsEbso}{\\num{" + benefit_of_semantics['gas_ebso'] +"}\\xspace} \n"

tex += "\\newcommand*{\\syrupOptimizesMore}{\\num{" + syrup_optimizes_more['syrup_optimizes_more'] +"}\\xspace} \n"
tex += "\\newcommand*{\\syrupOptimizesMoreSyrup}{\\num{" + syrup_optimizes_more['gas_syrup'] +"}\\xspace} \n"
tex += "\\newcommand*{\\syrupOptimizesMoreEbso}{\\num{" + syrup_optimizes_more['gas_ebso'] +"}\\xspace} \n"
print(tex)
