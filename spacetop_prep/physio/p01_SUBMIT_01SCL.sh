#!/bin/bash -l
#SBATCH --job-name=physio
#SBATCH --nodes=1
#SBATCH --task=4
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=01:30:00
#SBATCH -o ./log/physio03_%A_%a.o
#SBATCH -e ./log/physio03_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-14%5

conda activate biopac

PROJECT_DIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cue"
PHYSIO_DIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/physio/physio03_bids"
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
TTL_INDEX=1
SCL_EPOCH_START=-3
SCL_EPOCH_END=20

python ${PWD}/p01_grouplevel_01SCL.py \
--input-physiodir ${PHYSIO_DIR} \
--input-behdir ${BEH_DIR} \
--output-logdir ${OUTPUT_LOGDIR} \
--output-savedir ${OUTPUT_SAVEDIR} \
--metadata ${METADATA} \
--dictchannel ${CHANNELJSON} \
--slurm-id ${SLURM_ID} \
--slurm-stride ${STRIDE} \
--bids-zeropad ${ZEROPAD} \
--bids-task ${TASK} \
--event-name "event_stimuli" \
--prior-event "event_expectrating" \
--later-event "event_actualrating" \
--source-samplingrate 2000 \
--dest-samplingrate 25 \
--scl-epochstart ${SCL_EPOCH_START} \
--scl-epochend ${SCL_EPOCH_END} \
--ttl-index ${TTL_INDEX} \
--baselinecorrect True \
--exclude-sub 1 2 3 4 5 6
