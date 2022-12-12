#!/bin/bash -l
#SBATCH --job-name=physio01
#SBATCH --nodes=1
#SBATCH --task=1
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=00:15:00
#SBATCH -o ./log/physio01_%A_%a.o
#SBATCH -e ./log/physio01_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard

conda activate physio

INPUT_DIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/physio"
SUB_ZEROPAD=4
SES_ZEROPAD=2
LOG_DIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/log"

python ${PWD}/c01_bidsifysort.py \
--raw-physiodir ${INPUT_DIR} \
--sub-zeropad ${SUB_ZEROPAD} \
--ses-zeropad ${SES_ZEROPAD} \
--logdir ${LOG_DIR}
