import subprocess
import csv

step = 0
solvers = []

def print_step():
    global step
    print("\nstep " + str(step), end = ": ")
    step = step+1

def select_solvers():
    global solvers
    while solvers == []: 
        print("select either (z) Z3, (b) BCLT, (o) OMS, or (a) all ")
        
        solver_selection = input()
        
        if solver_selection == "z":  solvers = ["Z3"]
        elif solver_selection == "b": solvers = ["BCLT"]
        elif solver_selection == "o": solvers = ["OMS"]
        elif solver_selection == "a": solvers = ["Z3", "BCLT", "OMS"]

def query_csvsql(query, in_tables) :
    return subprocess.check_output(['csvsql'] + in_tables + ['--query', query], encoding='UTF-8')

print("-------------------------------------------------------------")
print("A Do-Nothing-Script for checking time and result distribution")
print("-------------------------------------------------------------")

print_step()
print("give path to results_*.csv")
path_to_results = input()

print_step()
print("give path to write time_result_distribution_*.csv")
path_to_aggregate = input()

print_step()
select_solvers()

for solver in solvers:
    query_grouped = f"""SELECT time_group AS up_to_sec, COUNT(*) as result_count
FROM
(
  SELECT block_id, solver_time_in_sec,
     CASE
     WHEN solver_time_in_sec BETWEEN 0 AND 1 THEN 1
     WHEN solver_time_in_sec BETWEEN 1 AND 2 THEN 2
     WHEN solver_time_in_sec BETWEEN 2 AND 3 THEN 3
     WHEN solver_time_in_sec BETWEEN 3 AND 4 THEN 4
     WHEN solver_time_in_sec BETWEEN 4 AND 5 THEN 5
     WHEN solver_time_in_sec BETWEEN 5 AND 6 THEN 6
     WHEN solver_time_in_sec BETWEEN 6 AND 7 THEN 7
     WHEN solver_time_in_sec BETWEEN 7 AND 8 THEN 8
     WHEN solver_time_in_sec BETWEEN 8 AND 9 THEN 9
     WHEN solver_time_in_sec BETWEEN 9 AND 10 THEN 10
     WHEN solver_time_in_sec BETWEEN 10 AND 11 THEN 11
     WHEN solver_time_in_sec BETWEEN 11 AND 12 THEN 12
     WHEN solver_time_in_sec BETWEEN 12 AND 13 THEN 13
     WHEN solver_time_in_sec BETWEEN 13 AND 14 THEN 14
     WHEN solver_time_in_sec BETWEEN 14 AND 15 THEN 15
     WHEN solver_time_in_sec BETWEEN 15 AND 20 THEN 20
     WHEN solver_time_in_sec BETWEEN 20 AND 25 THEN 25
     WHEN solver_time_in_sec BETWEEN 25 AND 30 THEN 30
     WHEN solver_time_in_sec BETWEEN 30 AND 35 THEN 35
     WHEN solver_time_in_sec BETWEEN 35 AND 40 THEN 40
     WHEN solver_time_in_sec BETWEEN 40 AND 45 THEN 45
     WHEN solver_time_in_sec BETWEEN 45 AND 50 THEN 50
     WHEN solver_time_in_sec BETWEEN 50 AND 55 THEN 55
     WHEN solver_time_in_sec BETWEEN 55 AND 60 THEN 60
     WHEN solver_time_in_sec BETWEEN 60 AND 90 THEN 90
     WHEN solver_time_in_sec BETWEEN 90 AND 120 THEN 120
     WHEN solver_time_in_sec BETWEEN 120 AND 300 THEN 300
     WHEN solver_time_in_sec BETWEEN 300 AND 600 THEN 600
     WHEN solver_time_in_sec >= 600 THEN 900
     END AS time_group
  FROM 'results_{solver}'
  WHERE shown_optimal = TRUE
) GROUP BY time_group
"""

    query_aggregated = f"""SELECT DISTINCT time_group AS up_to_sec,
COUNT(*) OVER (ORDER BY time_group) as result_count
FROM
(
  SELECT block_id, solver_time_in_sec,
     CASE
     WHEN solver_time_in_sec BETWEEN 0 AND 1 THEN 1
     WHEN solver_time_in_sec BETWEEN 1 AND 2 THEN 2
     WHEN solver_time_in_sec BETWEEN 2 AND 3 THEN 3
     WHEN solver_time_in_sec BETWEEN 3 AND 4 THEN 4
     WHEN solver_time_in_sec BETWEEN 4 AND 5 THEN 5
     WHEN solver_time_in_sec BETWEEN 5 AND 6 THEN 6
     WHEN solver_time_in_sec BETWEEN 6 AND 7 THEN 7
     WHEN solver_time_in_sec BETWEEN 7 AND 8 THEN 8
     WHEN solver_time_in_sec BETWEEN 8 AND 9 THEN 9
     WHEN solver_time_in_sec BETWEEN 9 AND 10 THEN 10
     WHEN solver_time_in_sec BETWEEN 10 AND 11 THEN 11
     WHEN solver_time_in_sec BETWEEN 11 AND 12 THEN 12
     WHEN solver_time_in_sec BETWEEN 12 AND 13 THEN 13
     WHEN solver_time_in_sec BETWEEN 13 AND 14 THEN 14
     WHEN solver_time_in_sec BETWEEN 14 AND 15 THEN 15
     WHEN solver_time_in_sec BETWEEN 15 AND 20 THEN 20
     WHEN solver_time_in_sec BETWEEN 20 AND 25 THEN 25
     WHEN solver_time_in_sec BETWEEN 25 AND 30 THEN 30
     WHEN solver_time_in_sec BETWEEN 30 AND 35 THEN 35
     WHEN solver_time_in_sec BETWEEN 35 AND 40 THEN 40
     WHEN solver_time_in_sec BETWEEN 40 AND 45 THEN 45
     WHEN solver_time_in_sec BETWEEN 45 AND 50 THEN 50
     WHEN solver_time_in_sec BETWEEN 50 AND 55 THEN 55
     WHEN solver_time_in_sec BETWEEN 55 AND 60 THEN 60
     WHEN solver_time_in_sec BETWEEN 60 AND 90 THEN 90
     WHEN solver_time_in_sec BETWEEN 90 AND 120 THEN 120
     WHEN solver_time_in_sec BETWEEN 120 AND 300 THEN 300
     WHEN solver_time_in_sec BETWEEN 300 AND 600 THEN 600
     WHEN solver_time_in_sec >= 600 THEN 900
     END AS time_group
  FROM 'results_{solver}'
  WHERE shown_optimal = TRUE
)"""
    
    time_result_distribution = query_csvsql(query_aggregated, [f'{path_to_results}/results_{solver}.csv'])

    output_file = path_to_aggregate + f"/time_result_distribution_{solver}.csv"   
    out = open(output_file, "w")
    out.write(time_result_distribution)
    out.close()
    
    print("Computed results for " + solver + " stored at " + output_file)
