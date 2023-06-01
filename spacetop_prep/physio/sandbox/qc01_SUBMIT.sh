#!/bin/bash -l
#SBATCH --job-name=physio
#SBATCH --nodes=1
#SBATCH --task=1
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=10:30:00
#SBATCH -o ./log/qcphysio02_%A_%a.o
#SBATCH -e ./log/qcphysio02_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-14%4
##14%5

conda activate biopac

# NOTE: User, change parameter
TOPDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/physio"
SLURM_ID=${SLURM_ARRAY_TASK_ID}
STRIDE=10
SUB_ZEROPAD=4
SAVEDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cue/analysis/physio/qc'

python ${PWD}/qc01_outlierdetection.py \
--topdir ${TOPDIR} \
--slurm-id ${SLURM_ID} \
--stride ${STRIDE} \
--savedir ${SAVEDIR} \
--sub-zeropad ${SUB_ZEROPAD} \
--exclude-sub 199
