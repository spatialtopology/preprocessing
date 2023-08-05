#!/bin/bash -l
#SBATCH --job-name=heatmap
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --mem-per-cpu=40G
#SBATCH --time=01:00:00
#SBATCH -o ./logcorr/heatmap_%A_%a.o
#SBATCH -e ./logcorr/heatmap_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1

mkdir -p ./logcorr

conda init bash

conda activate biopac

# Check if SLURM_ARRAY_TASK_ID is not set or is empty
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
    # Set SLURM_ARRAY_TASK_ID to a default value, e.g., 1
    SLURM_ARRAY_TASK_ID=1
fi

hostname
echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
# MAINDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep/qcplot"
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/scripts/biopac/wasabi-prep/spacetop_prep/qcplot'
# IMGDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/runwisecorr"
IMGDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/runwisecorr'

BADRUNFNAME="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep/qcplot/task-social_bad_runs.json"
NOTINTENDFNAME="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep/qcplot/not_in_intendedFor.json"

python ${MAINDIR}/runwisecorr/corr03_heatmap.py \
--slurm-id ${ID} \
--img-dir ${IMGDIR} \
--bad-run ${BADRUNFNAME} \
--no-intend ${NOTINTENDFNAME} \
--task "task-"