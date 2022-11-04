#!/bin/bash -l
#SBATCH --job-name=physio01
#SBATCH --nodes=1
#SBATCH --task=4
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=03:00:00
#SBATCH -o ./log/biopac_%A_%a.o
#SBATCH -e ./log/biopac_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard

conda activate biopac

CLUSTER='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/physio'
SUB_NUM=4
RUN_NUM=2
python ${PWD}/c01_bidsify_discovery.py ${CLUSTER} ${SUB_NUM} ${RUN_NUM}
