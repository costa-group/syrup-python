print("------------------------------------------------")
print("A Do-Nothing-Script for synching the solvers    ")
print("------------------------------------------------")

def sync_to_cluster(filename, destination) :
    print("synch " + filename + " to cluster.")
    print("rsync -av -e 'ssh mschett@tails.cs.ucl.ac.uk ssh' "
          + filename +
          " mschett@vic.cs.ucl.ac.uk:/home/mschett/" + destination)

remote_path_to_solvers = "syrup-backend/solvers/"
print("Z3:")
path_to_Z3="/home/maria/software/z3-z3-4.8.7/build/z3"
sync_to_cluster(path_to_Z3, remote_path_to_solvers)
print()

print("BCLT:")
path_to_BCLT="/home/maria/syrup-paper/implementation/barcelogic"
sync_to_cluster(path_to_BCLT, remote_path_to_solvers)
print()

print("OMS:")
path_to_OMS="/home/maria/research/projects/syrup/optiMathSAT/optimathsat-1.6.3-linux-64-bit/bin/optimathsat"
sync_to_cluster(path_to_OMS, remote_path_to_solvers)
print("  ")
