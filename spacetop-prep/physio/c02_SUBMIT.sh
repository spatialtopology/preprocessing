#!/bin/bash -l
#SBATCH --job-name=physio
#SBATCH --nodes=1
#SBATCH --task=4
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=05:30:00
#SBATCH -o ./log/physio02_%A_%a.o
#SBATCH -e ./log/physio02_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=3-14%5

conda activate biopac

CLUSTER="discovery" # local
SLURM_IND=${SLURM_ARRAY_TASK_ID}
TASK="task-social"
CUTOFF=300
python ${PWD}/c02_save_separate_run.py ${CLUSTER} ${SLURM_IND} ${TASK} ${CUTOFF}
