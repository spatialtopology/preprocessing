#!/bin/bash -l
#SBATCH --job-name=plot
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=24:00:00
#SBATCH -o ./log/plot/np_%A_%a.o
#SBATCH -e ./log/plot/np_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
# Each array index should be a subject
#SBATCH --array=1-NSUBJECTS%10

mkdir -p ./log/plot

conda init
conda activate YOUR_ENVIRONMENT

# FOR DEBUGGING:
# Check if SLURM_ARRAY_TASK_ID is not set or is empty
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
    # Set SLURM_ARRAY_TASK_ID to a default value, e.g., 1
    SLURM_ARRAY_TASK_ID=1
fi

echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}

# Replace all directories below with your own
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='MAIN_STUDY_DIRECTORY'
FMRIPREPDIR='../derivatives/fmriprep'
OUTPUTDIR='../derivatives/fmriprep_qc/numpy_bold'
python ${MAINDIR}/../spacetop_prep/qcplot/boldcorrelation/qc01_saveniinumpy.py \
--slurm-id ${ID} \
--fmriprepdir ${FMRIPREPDIR} \
--outputdir ${OUTPUTDIR}
