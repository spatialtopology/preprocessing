#!/bin/bash -l
#SBATCH --job-name=spctp_prprc
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=06:00:00
#SBATCH -o ./log/preproc_%A_%a.o
#SBATCH -e ./log/preproc_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-17%5
## --array=1-17%5


#source /optnfs/common/miniconda3/etc/profile.d/conda.sh
#conda activate spacetop_env

# parameters _________________________________________________________
IMAGE="/dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-0.14.2.sif"
MAINDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop"
BIDS_DIRECTORY="${MAINDIR}/dartmouth"
SCRATCH_DIR="/scratch/f0042x1/spacetop/preproc"
SCRATCH_WORK="${SCRATCH_DIR}/work"
OUTPUT_DIR="${MAINDIR}/dartmouth/derivatives/mriqc"
OUTPUT_WORK="${OUTPUT_DIR}/work"

subjects=("0001" "0002" "0003" "0004" "0005" "0006" "0007" "0008" "0009" "0010" \
"0011" "0013" "0014" "0015" "0016" "0017" "0020")
# SUBJ_IND=$((SLURM_ARRAY_TASK_ID / 4))
#echo $SUBJ_IND
#SES_IND=$((SLURM_ARRAY_TASK_ID % 4 + 1))
#echo $SES_IND 
#SUBJ=${subjects[$SUBJ_IND]}
SUBJ=${subjects[$SLURM_ARRAY_TASK_ID]}
echo "array id: " ${SLURM_ARRAY_TASK_ID}, "subject id: " ${SUBJ}, "session id: " ${SES_IND}

# mriqc command _________________________________________________________
echo $PATH
echo $PYTHONPATH
unset $PYTHONPATH;

#singularity run -B /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth:/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth  /dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-0.14.2.sif /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth/derivatives participant --participant_label 0005

singularity run  \
-B ${BIDS_DIRECTORY}:${BIDS_DIRECTORY} \
-B ${OUTPUT_DIR}:${OUTPUT_DIR} \
-B ${OUTPUT_WORK}:${OUTPUT_WORK} \
${IMAGE} \
--session-id 02 \
-w ${OUTPUT_WORK} \
--n_procs 16 \
--mem_gb 8 \
--ica \
--start-idx 6 \
--fft-spikes-detector \
--write-graph \
--correct-slice-timing \
--fd_thres 0.9 \
${BIDS_DIRECTORY} ${OUTPUT_DIR} participant --participant_label ${SUBJ}

echo "COMPLETING mriqc ... COPYING over"

# cp ${SCRATCH_DIR} ${OUTPUT_DIR}
# cp ${SCRATCH_WORK} ${OUTPUT_WORK}

echo "process complete"

