#$ -S /bin/bash
#$ -cwd           # Set the working directory for the job to the current directory
#$ -l h_rt=2:00:00 # Request runtime
#$ -l h_vmem=2G   # Request 1GB RAM
#$ -l tmem=2G     # Request 1GB RAM
#$ -j y           # Join stdout and stderr
#$ -o /dev/null   # Do not create files for stdout
#$ -t 1-46966:4
BATCH_MAX="$((${SGE_TASK_ID}+3))"
for i in `seq ${SGE_TASK_ID} $((BATCH_MAX <= 46966 ? BATCH_MAX : 46966))`
do
  PATH_TO_INPUT=/home/mschett/syrup-eval/$(sed "${i}q;d" /home/mschett/syrup-eval/input-list.txt)
  /home/mschett/syrup-backend/run_OMS.sh -timeout 900 -omit-csv-header -scale-sk-sz 200 $PATH_TO_INPUT > /home/mschett/syrup-eval/stack-size/scale-200/results/result_OMS_${i}.json 2>&1
done
