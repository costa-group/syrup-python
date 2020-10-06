import os
import math
import datetime

step = 0
remote_path_to_syrup = "/home/mschett/syrup-backend"

def print_step():
    global step
    print("\nstep " + str(step), end = ": ")
    step = step+1

def cluster_log_in():
    print_step()
    print("if not in CS network login to tails first")
    print("ssh mschett@tails.cs.ucl.ac.uk")
    print("current password works")
    
    print_step()
    print("from there, log in to login node vic")
    print("ssh vic.cs.ucl.ac.uk")

def synch_from_cluster(source, target):
    print("synch " + source + " from cluster.")
    print("rsync -av -e 'ssh mschett@tails.cs.ucl.ac.uk ssh' "
          "mschett@vic.cs.ucl.ac.uk:" + source + " " +
          target
    )
    
def synch_to_cluster(filename, destination):
    print("synch " + filename + " to cluster.")
    print("rsync -av -e 'ssh mschett@tails.cs.ucl.ac.uk ssh' "
          + filename +
          " mschett@vic.cs.ucl.ac.uk:" + destination)

solvers = ["Z3", "BCLT", "OMS"]
    
print("------------------------------------------------")
print("A Do-Nothing-Script for finding missing results ")
print("------------------------------------------------")


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
print("[on cluster]: absolute path to files listed in missing listd")
remote_path_to_data_set = input()

print_step()
print("give local path to local results file.")
local_path_to_results_folder = input()

for solver in solvers:
    print_step()
    print("[on cluster] create list of all exisiting results")
    print(f'find results/ -name "*_{solver}*" -size +0 > result-list_{solver}.txt')
    input("done? ")

print_step()
synch_from_cluster(remote_path_to_run_script + "/result-list_{" + ','.join(solvers) + "}.txt", local_path_to_results_folder)
input("done? ")

input_list = "input-list.txt"
total_tasks = {}

for solver in solvers:
    print_step()
    print("Find missing results")
    with open(local_path_to_results_folder + "/" + input_list) as inpt:
        with open(local_path_to_results_folder+  f'/result-list_{solver}.txt') as rslt:
            with open(local_path_to_results_folder + f'/missing-list_{solver}.txt', 'w') as missing:
                rslt_content = rslt.read()
                rslt_count = len(rslt_content.splitlines())
                i = 1
                missing_count = 0
                for row in inpt:
                    if not f'_{i}.' in rslt_content:
                        missing.write(f"{i},{row}")
                        missing_count = missing_count + 1
                    i = i + 1
                print(f"Found {missing_count} missing results out of {i-1} inputs for {solver}")
                print(f"sanity check: {i-1} = {missing_count+rslt_count}")
                total_tasks[solver] = missing_count
                
print_step()
print("Sync missing lists to cluster")
synch_to_cluster(local_path_to_results_folder + "/missing-list_{" + ','.join(solvers) + "}.txt", remote_path_to_run_script)
input("done? ")

print_step()
print("Create run scripts")

print_step()
print("give timeout in seconds")
time_out_in_sec = int(input())

print_step()
print("give real time per batch in minutes")
real_batch_time_in_sec = int(input()) * 60

batch_size = math.floor(real_batch_time_in_sec / time_out_in_sec)
print("batch size: " + str(batch_size))

for solver in solvers:
    call = remote_path_to_syrup + "/run_" + solver + ".sh -timeout " + str(time_out_in_sec) + " -omit-csv-header"
    request_time = str(datetime.timedelta(seconds=real_batch_time_in_sec * 2))
    line = '$(sed "${i}q;d" ' + f'missing-list_{solver}.txt' + ')'
    splitline = '(${LINE//,/ })'
    path_to_input = '${SPLITLINE[1]}'
    index = '${SPLITLINE[0]}'
    path_to_output = f'{remote_path_to_results}/result_' + solver + '_${INDEX}.json'
    
    batch_max = '"$((${SGE_TASK_ID}' + f'+{batch_size-1}))"'
    batch_range = '`seq ${SGE_TASK_ID} ' + f'$((BATCH_MAX <= {total_tasks[solver]} ? BATCH_MAX : {total_tasks[solver]}))`'

    run_script_content = f'''#$ -S /bin/bash
#$ -cwd           # Set the working directory for the job to the current directory
#$ -l h_rt={request_time} # Request runtime
#$ -l h_vmem=2G   # Request 2GB RAM
#$ -l tmem=2G     # Request 2GB RAM
#$ -j y           # Join stdout and stderr
#$ -o /dev/null   # Do not create files for stdout
#$ -t 1-{total_tasks[solver]}:{batch_size}
BATCH_MAX={batch_max}
for i in {batch_range}
do
  LINE={line}
  SPLITLINE={splitline}
  PATH_TO_INPUT={remote_path_to_data_set}/{path_to_input}
  INDEX={index}
  {call} $PATH_TO_INPUT > {path_to_output} 2>&1
done
'''

    run_script_name = "run_missing_" + solver + ".sh"
    local_path_to_run_script = local_path_to_results_folder + "/" + run_script_name

    run_script = open(local_path_to_run_script, "w")
    run_script.write(run_script_content)
    run_script.close()

print_step()
local_path_to_run_scripts = local_path_to_results_folder + "/" + "run_missing_{" + ','.join(solvers) + '}.sh'
synch_to_cluster(local_path_to_run_scripts, remote_path_to_run_script)
input("done? ")

print_step()
print("[on cluster]: check make run script executable")
run_script_names = ["run_missing_" + solver + ".sh" for solver in solvers]
print("chmod a+x " + ' '.join(run_script_names))
input("done?")

for solver in solvers:
    print_step()
    run_script_name = "run_missing_" + solver + ".sh"
    print("[on cluster]: start evaluation")
    print("qsub " + run_script_name)
