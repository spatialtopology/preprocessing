#!/bin/bash -l
#SBATCH --job-name=fdmean
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem-per-cpu=20G
#SBATCH --time=02:00:00
#SBATCH -o ./logfd/fdmean_%A_%a.o
#SBATCH -e ./logfd/fdmean_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-100%30

mkdir -p ./logfd

conda init bash

conda activate biopac

# Check if SLURM_ARRAY_TASK_ID is not set or is empty
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
    # Set SLURM_ARRAY_TASK_ID to a default value, e.g., 1
    SLURM_ARRAY_TASK_ID=1
fi

echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/scripts/biopac/wasabi-prep/spacetop_prep/qcplot'
FMRIPREPDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/'
SAVEDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc'

python ${MAINDIR}/fdmean/fdmean_painruns.py \
--slurm-id ${ID} \
--fmriprepdir ${FMRIPREPDIR} \
--savedir ${SAVEDIR}
