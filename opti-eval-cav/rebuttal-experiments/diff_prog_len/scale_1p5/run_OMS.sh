#$ -S /bin/bash
#$ -cwd           # Set the working directory for the job to the current directory
#$ -l h_rt=1:00:00 # Request runtime
#$ -l h_vmem=2G   # Request 1GB RAM
#$ -l tmem=2G     # Request 1GB RAM
#$ -j y           # Join stdout and stderr
#$ -o /dev/null   # Do not create files for stdout
#$ -t 1-2000:2
BATCH_MAX="$((${SGE_TASK_ID}+1))"
for i in `seq ${SGE_TASK_ID} $((BATCH_MAX <= 2000 ? BATCH_MAX : 2000))`
do
  PATH_TO_INPUT=$(sed "${i}q;d" input-list.txt)
  /home/mschett/opti/run_OMS.sh -timeout 900 -omit-csv-header -scale-progr-len 150 $PATH_TO_INPUT > /home/mschett/opti-eval/rebuttal-experiments/results-1-5/result_OMS_${i}.json 2>&1
done
