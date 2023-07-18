#!/bin/bash -l
#SBATCH --job-name=physio
#SBATCH --nodes=1
#SBATCH --task=1
#SBATCH --mem-per-cpu=16gb
#SBATCH --time=05:30:00
#SBATCH -o ./log/physio02_%A_%a.o
#SBATCH -e ./log/physio02_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-14%5

conda activate physio

# NOTE: User, change parameter
TOPDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/physio"
METADATA="/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social/data/spacetop_task-social_run-metadata.csv"
SLURM_ID=${SLURM_ARRAY_TASK_ID}
STRIDE=10
SUB_ZEROPAD=4
TASK="task-social"
CUTOFF=300
CHANGETASK="./c02_changetaskname.json"
CHANGECOL="./c02_changecolumn.json"

python ${PWD}/c02_save_separate_run.py \
--topdir ${TOPDIR} \
--metadata ${METADATA} \
--slurm_id ${SLURM_ID} \
--stride ${STRIDE} \
--sub-zeropad ${SUB_ZEROPAD} \
--task ${TASK} \
--run-cutoff ${CUTOFF} \
--colnamechange ${CHANGECOL} \
--tasknamechange ${CHANGETASK} \
--exclude_sub 1 2 3 4 5 6
