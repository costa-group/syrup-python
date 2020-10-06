step = 0

def print_step():
    global step
    print("\nstep " + str(step), end = ": ")
    step = step+1

def results_from_cluster(source, target):
    print("synch " + source + " from cluster.")
    print("rsync -av -e 'ssh mschett@tails.cs.ucl.ac.uk ssh' "
          "mschett@vic.cs.ucl.ac.uk:" + source + " " +
          target
    )
    
print("------------------------------------------------")
print("A Do-Nothing-Script for csv-ing an evaluation   ")
print("------------------------------------------------")

solvers = ["Z3", "BCLT", "OMS"]

print_step()
print("[on cluster]: give path to results folder")
remote_path_to_results_folder = input()

print_step()
print("[on cluster]: give path to combined results csv-file")
remote_path_to_results_csv_folder = input()

print_step()
print("combine to csv")
print("cd " + remote_path_to_results_csv_folder)

for solver in solvers:
    print_step()
    print("create results file for " + solver)
    csv_header = '"block_id,target_gas_cost,shown_optimal,no_model_found,source_gas_cost,saved_gas,solver_time_in_sec,target_disasm,target_opcode"'
    print('echo '+ csv_header + f' > {remote_path_to_results_csv_folder}/results_{solver}.csv')
    input("done?")
    print_step()
    print("collect results for " + solver)
    print(f'find {remote_path_to_results_folder} -name "result_{solver}*" -exec cat ' +'"{}"' + f' \; >> {remote_path_to_results_csv_folder}/results_{solver}.csv')
    input("done?")

print_step()
print("give path to local evaluation folder")
local_path_to_eval = input()
    
print_step()
print("sync results from cluster")
result_files = "results_{" + ','.join(solvers) + '}.csv'
results_from_cluster(remote_path_to_results_csv_folder + "/" + result_files, local_path_to_eval)
input("done?")

print_step()
print("upload results to svn")
