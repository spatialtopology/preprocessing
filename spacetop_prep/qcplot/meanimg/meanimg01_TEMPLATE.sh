#!/bin/bash -l
#SBATCH --job-name=glm
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=01:00:00
#SBATCH -o ./log/glm/glm_%A_%a.o
#SBATCH -e ./log/glm/glm_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
# Your array should index your subjects
#SBATCH --array=1-NSUBJECTS%10

mkdir -p ./log/glm

conda init
conda activate YOUR_ENVIRONMENT

# Check if SLURM_ARRAY_TASK_ID is not set or is empty
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
    # Set SLURM_ARRAY_TASK_ID to a default value, e.g., 1
    SLURM_ARRAY_TASK_ID=1
fi

echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='MAIN_STUDY_DIRECTORY'
SAVEDIR='../derivatives/fmriprep_qc/'
# This should be your BIDS value for task e.g., 'social', for task-social
TASK=''

python ${MAINDIR}/../spacetop_prep/qcplot/meanimg/plotmeanimg.py --slurm-id ${ID} --task ${TASK} --save_dir ${SAVEDIR}