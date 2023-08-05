#!/bin/bash -l
#SBATCH --job-name=glm
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=01:00:00
#SBATCH -o ./qc/qc_%A_%a.o
#SBATCH -e ./qc/qc_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-13%10
#33%10

conda init
conda activate biopac

# Check if SLURM_ARRAY_TASK_ID is not set or is empty
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
    # Set SLURM_ARRAY_TASK_ID to a default value, e.g., 1
    SLURM_ARRAY_TASK_ID=1
fi

echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI'
SAVEDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/'
# PYBIDSDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/1080_wasabi/1080_wasabi_BIDSLayout'

# python ${MAINDIR}/scripts/biopac/wasabi-prep/spacetop_prep/qcplot/meanimg/plotmeanimg.py --slurm-id ${ID} --task '' --save_dir ${SAVEDIR} --pybids_db ${PYBIDSDIR}
python ${MAINDIR}/scripts/biopac/wasabi-prep/spacetop_prep/qcplot/meanimg/plotmeanimg.py --slurm-id ${ID} --task '' --save_dir ${SAVEDIR}