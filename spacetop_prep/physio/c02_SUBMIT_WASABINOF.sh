#!/bin/bash -l

#SBATCH --job-name=[wasabi_physio02]
#SBATCH -o ./log/wasabi_physio02_%A_%a.txt
#SBATCH -e ./log/wasabi_physio02_%A_%a.err
#SBATCH --nodes=1
#SBATCH --task=1
#SBATCH --mem-per-cpu=32gb
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --time=7-01:00:00
#SBATCH --array=6
##SBATCH --array=0-9,1001,1002
#SBATCH --mail-type=FAIL,END
#SBATCH --requeue

# WASABInof_split_runs_and_extract_TTLs.sh
# Split Runs and Extract TTLs
# Run this in the SLURM scheduler

# Had to add these lines to initialize conda
conda init bash
source ~/.bashrc

conda activate biopac

# Added this
# Create log directories if one doesn't exist
if [ ! -e ${PWD}/log ]; then
    mkdir -p ${PWD}/log
fi

# NOTE: User, change parameter
TOPDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq"
METADATA="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/wasabi_nof_run-metadata2.csv"
SLURM_ID=${SLURM_ARRAY_TASK_ID}
#SLURM_ID=0
STRIDE=1
SUB_ZEROPAD=5 # Does this pertain to the subject ID? Which subject ID is it using, the acq file or the
TASK="task-bodymap"
CUTOFF=300 # This is in seconds, not TRs. This is just shorter than the pinellocalizer, which is our shortest sequence.
CHANGETASK="./c02_changetaskname.json"
CHANGECOL="./c02_changecolumn_WASABI.json"

# Edit c02_changecolumn.json to reflect biopac channels

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
--exclude-sub 199
