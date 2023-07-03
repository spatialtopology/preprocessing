#!/bin/bash -l
#SBATCH --job-name=corr
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --mem-per-cpu=40G
#SBATCH --time=01:00:00
#SBATCH -o ./logcorr/np_%A_%a.o
#SBATCH -e ./logcorr/np_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-13%10

conda activate spacetop_env
echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
# QCDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cue'
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep/qcplot'
QCDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/spacetop_data/derivatives/fmriprep_qc'
FMRIPREPDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'
SAVEDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/spacetop_data/derivatives/fmriprep_qc/runwisecorr'
SCRATCHDIR='/dartfs-hpc/scratch/f0042x1'
CANLABDIR='/dartfs-hpc/rc/lab/C/CANlab/modules/CanlabCore'
python ${MAINDIR}/runwisecorr/runwisecorr.py \
--slurm-id ${ID} \
--qcdir ${QCDIR} \
--fmriprepdir ${FMRIPREPDIR} \
--savedir ${SAVEDIR} \
--scratchdir ${SCRATCHDIR} \
--canlabdir ${CANLABDIR}
