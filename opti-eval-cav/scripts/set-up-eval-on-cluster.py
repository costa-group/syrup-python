import datetime
import subprocess
import math

step = 0
solvers = []
tool = "syrup-backend"
remote_path_to_syrup = "/home/mschett/syrup-backend"

def print_step():
    global step
    print("\nstep " + str(step), end = ": ")
    step = step+1

def select_solver():
    global solvers
    while solvers == []: 
        print("select either (z) Z3, (b) BCLT, (o) OMS, or (a) all ")
        
        solver_selection = input()
        
        if solver_selection == "z":  solvers = ["Z3"]
        elif solver_selection == "b": solvers = ["BCLT"]
        elif solver_selection == "o": solvers = ["OMS"]
        elif solver_selection == "a": solvers = ["Z3", "BCLT", "OMS"]

def cluster_log_in():
    print_step()
    print("if not in CS network login to tails first")
    print("ssh mschett@tails.cs.ucl.ac.uk")
    print("current password works")
    
    print_step()
    print("from there, log in to login node vic")
    print("ssh vic.cs.ucl.ac.uk")

def synch_to_cluster(filename, destination):
    print("synch " + filename + " to cluster.")
    print("rsync -av -e 'ssh mschett@tails.cs.ucl.ac.uk ssh' "
          + filename +
          " mschett@vic.cs.ucl.ac.uk:" + destination)

def enter_path():
    return input()
        
print("------------------------------------------------")
print("A Do-Nothing-Script for setting up an evaluation")
print("------------------------------------------------")

print_step()
print("[on cluster]: check executable is up-to-date")

print_step()
print("[on cluster]: path folder for run script")
remote_path_to_run_script = input()

print_step()
print("[on cluster]: path to results folder")
remote_path_to_results = input()

print_step()
print("[on cluster]: path to input_list")
remote_path_to_input_list = input()

print_step()
print("[on cluster]: absolute path to files listed in input_list")
remote_path_to_data_set = input()

input_list = "input-list.txt"
print_step()
print("[on cluster]: count input.json.")
print("wc -l " + input_list)
total_tasks = int(input("count of input.json? "))

print_step()
select_solver()
print("selected " + ','.join(solvers) + ".")

print_step()
print("give timeout in seconds")
time_out_in_sec = int(input())

print_step()
print("give real time per batch in minutes")
real_batch_time_in_sec = int(input()) * 60

batch_size = math.floor(real_batch_time_in_sec / time_out_in_sec)
print("batch size: " + str(batch_size))

print_step()
print("give extra flags if required, enter otherwise")
flag = input()

print_step()
print("prepare run script.")

print_step()
print("give local path to run script")
local_folder_to_run_script = enter_path()

for solver in solvers:
    call = remote_path_to_syrup + "/run_" + solver + ".sh -timeout " + str(time_out_in_sec) + " -omit-csv-header " + flag
    request_time = str(datetime.timedelta(seconds=real_batch_time_in_sec * 2))
    path_to_input = '$(sed "${i}q;d" ' + remote_path_to_input_list + '/' + input_list + ')'
    path_to_output = f'{remote_path_to_results}/result_' + solver + '_${i}.json'

    batch_max = '"$((${SGE_TASK_ID}' + f'+{batch_size-1}))"'
    batch_range = '`seq ${SGE_TASK_ID} ' + f'$((BATCH_MAX <= {total_tasks} ? BATCH_MAX : {total_tasks}))`'

    run_script_content = f'''#$ -S /bin/bash
#$ -cwd           # Set the working directory for the job to the current directory
#$ -l h_rt={request_time} # Request runtime
#$ -l h_vmem=2G   # Request 1GB RAM
#$ -l tmem=2G     # Request 1GB RAM
#$ -j y           # Join stdout and stderr
#$ -o /dev/null   # Do not create files for stdout
#$ -t 1-{total_tasks}:{batch_size}
BATCH_MAX={batch_max}
for i in {batch_range}
do
  PATH_TO_INPUT={remote_path_to_data_set}/{path_to_input}
  {call} $PATH_TO_INPUT > {path_to_output} 2>&1
done
'''

    run_script_name = "run_" + solver + ".sh"
    local_path_to_run_script = local_folder_to_run_script + "/" + run_script_name

    run_script = open(local_path_to_run_script, "w")
    run_script.write(run_script_content)
    run_script.close()

print_step()
local_path_to_run_scripts = local_folder_to_run_script + "/" + "run_{" + ','.join(solvers) + '}.sh'
synch_to_cluster(local_path_to_run_scripts, remote_path_to_run_script)

print_step()
print("[on cluster]: check " + input_list)
input("done?")

print_step()
print("[on cluster]: check make run script executable")
run_script_names = ["run_" + solver + ".sh" for solver in solvers]
print("chmod a+x " + ' '.join(run_script_names))
input("done?")

for solver in solvers:
    print_step()
    run_script_name = "run_" + solver + ".sh"
    print("[on cluster]: start evaluation")
    print("qsub " + run_script_name)

print_step()
print("sanity check start of evaluation")

print_step()
print("[on cluster]: check status of evaluation")
print("find . -name result_*.json | wc -l ")

