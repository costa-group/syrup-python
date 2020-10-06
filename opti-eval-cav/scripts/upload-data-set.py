import os

step = 0

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

def synch_to_cluster(filename, destination):
    print("synch " + filename + " to cluster.")
    print("rsync -av -e 'ssh mschett@tails.cs.ucl.ac.uk ssh' "
          + filename +
          " mschett@vic.cs.ucl.ac.uk:/home/mschett/" + destination)
    
print("------------------------------------------------")
print("A Do-Nothing-Script for uploading a data set    ")
print("------------------------------------------------")

print_step()
print("give a name to describe the purpose of the evaluation.")
name = input()

print_step()
print("login to cluster.")
cluster_log_in()
input("done? ")

print_step()
print("[on cluster]: create destination for evaluation")
print("cd /home/mschett/syrup-eval/")
print("mkdir " + name)
remote_path_to_data_set = "syrup-eval/" + name
input("done? ")

print_step()
print("give local path to data set.")
local_path_to_data_set = input()

print_step()
synch_to_cluster(local_path_to_data_set, remote_path_to_data_set)
input("done? ")

input_list = "input-list.txt"

print_step()
print("generate a list with paths to every input.json.")
print("cd " + os.path.dirname(local_path_to_data_set))
print(f"find {os.path.basename(local_path_to_data_set)} -name input.json > " + input_list)
local_path_to_input_list = os.path.dirname(local_path_to_data_set) + "/" + input_list
input("done? ")

print_step()
print("sanity check and count input.json.")
print("wc -l " + input_list)
total = int(input("count of input.json? "))

if total > 10000:
    print_step()
    print("email Ed to warn him of job.")

print_step()
synch_to_cluster(local_path_to_input_list, remote_path_to_data_set)
input("done? ")
