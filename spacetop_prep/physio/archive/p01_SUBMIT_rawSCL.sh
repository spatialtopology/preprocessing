#!/bin/bash -l
#SBATCH --job-name=physio
#SBATCH --nodes=1
#SBATCH --task=4
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=05:30:00
#SBATCH -o ./log/physio02_%A_%a.o
#SBATCH -e ./log/physio02_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-14%5

conda activate biopac

# CLUSTER="discovery" # local
PROJECT_DIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social"
PHYSIO_DIR="${PROJECT_DIR}/data/physio/physio03_bids"
BEH_DIR="${PROJECT_DIR}/data/beh/beh02_preproc"
OUTPUT_LOGDIR="${PROJECT_DIR}/scripts/logcenter"
OUTPUT_SAVEDIR="${PROJECT_DIR}/analysis/physio"
METADATA="${PROJECT_DIR}/data/spacetop_task-social_run-metadata.csv"
CHANNELJSON="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep/physio/p01_channel.json"
SLURM_ID=${SLURM_ARRAY_TASK_ID}
STRIDE=10
ZEROPAD=4
TASK="task-cue"
SAMPLINGRATE=2000
TTL_INDEX=2
TONIC_EPOCH_START=-1
TONIC_EPOCH_END=20


# TODO: these metadata -- cutoff, sampling rate -- could be pulled in from json sidecars
#  -m pdb
python ${PWD}/p01_group_level_analysis_rawSCL.py \
--input-physiodir ${PHYSIO_DIR} \
--input-behdir ${BEH_DIR} \
--output-logdir ${OUTPUT_LOGDIR} \
--output-savedir ${OUTPUT_SAVEDIR} \
--metadata ${METADATA} \
--dictchannel ${CHANNELJSON} \
--slurm-id ${SLURM_ID} \
--stride ${STRIDE} \
--zeropad ${ZEROPAD} \
--task ${TASK} \
-sr ${SAMPLINGRATE} \
--ttl-index ${TTL_INDEX} \
--tonic-epochstart ${TONIC_EPOCH_START} \
--tonic-epochend ${TONIC_EPOCH_END}

# required parameters
# input_physio_dir
# input_beh_dir
# top_dir needed?
# out_logdir
# out_savedir
# run metadata
# list of columns to extract from behavioral data
# change channel names
