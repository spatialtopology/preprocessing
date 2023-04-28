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
SLURM_ID=${SLURM_ARRAY_TASK_ID}
STRIDE=10
SUB_ZEROPAD=4
SAVEDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cue/figure/physio/qc'

python ${PWD}/qc01_outlierdetection.py \
--topdir ${TOPDIR} \
--slurm_id ${SLURM_ID} \
--stride ${STRIDE} \
--savedir ${SAVEDIR} \
--sub-zeropad ${SUB_ZEROPAD} \
--exclude_sub 1 2 3 4 5 6
