#!/bin/bash -l
#SBATCH --job-name=dtld
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --partition=standard
#SBATCH -o ./log/datalad_%A_%a.o
#SBATCH -e ./log/datalad_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --array=4-10%3

cd /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth

source /optnfs/common/miniconda3/etc/profile.d/conda.sh
conda activate spacetop_env

datalad --version
git-annex version

subjects=("sub-0001" "sub-0002" "sub-0003" "sub-0004" "sub-0005" \
"sub-0006" "sub-0007" "sub-0008" "sub-0009" "sub-0010")
echo ${SLURM_ARRAY_TASK_ID}
SUBJ=${subjects[$SLURM_ARRAY_TASK_ID]}
echo ${SUBJ}
datalad get ${SUBJ}
echo "process complete"
