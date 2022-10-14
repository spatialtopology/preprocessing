#!/bin/bash -l
#SBATCH --job-name=spctp_fmriprp
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=2-00:00:00
#SBATCH -o ./log/preproc_%A_%a.o
#SBATCH -e ./log/preproc_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=6
## --array=1-17%5


#source /optnfs/common/miniconda3/etc/profile.d/conda.sh
#conda activate spacetop_env

# parameters _________________________________________________________
CONTAINER_IMAGE="/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep-20.2.1-LTS.sif"
MAINDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop"
BIDS_DIRECTORY="${MAINDIR}/dartmouth"
# TODO: /dartfs-hpc/scratch/f0042x1
SCRATCH_DIR="/scratch/f0042x1/spacetop/preproc"
SCRATCH_WORK="${SCRATCH_DIR}/work"
OUTPUT_DIR="${MAINDIR}/derivatives/dartmouth/fmriprep"
OUTPUT_WORK="${OUTPUT_DIR}/work"

subjects=("0001" "0002" "0003" "0004" "0005" "0006" "0007" "0008" "0009" "0010" \
"0011" "0013" "0014" "0015" "0016" "0017" "0020")
PARTICIPANT_LABEL=${subjects[$((SLURM_ARRAY_TASK_ID - 1 ))]}
echo "array id: " ${SLURM_ARRAY_TASK_ID}, "subject id: " ${PARTICIPANT_LABEL}

# mriqc command _________________________________________________________
echo $PYTHONPATH
unset $PYTHONPATH;
conda activate spacetop_env
rm -rf .heudiconv .git/annex/transfer
datalad clean

module purge
module load freesurfer/6.0.0

#singularity run -B /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth:/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth  /dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-0.14.2.sif /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth/derivatives participant --participant_label 0005
unset $PYTHONPATH;

singularity run -B ${BIDS_DIRECTORY}:${BIDS_DIRECTORY} \
-B ${OUTPUT_DIR}:${OUTPUT_DIR} \
-B ${OUTPUT_WORK}:${OUTPUT_WORK} \
-B /optnfs/freesurfer:/optnfs/freesurfer \
${CONTAINER_IMAGE} \
${BIDS_DIRECTORY} ${OUTPUT_DIR} participant --participant_label ${PARTICIPANT_LABEL} -w ${OUTPUT_WORK} \
--task-id social \
--write-graph \
--n-cpus 16 \
--notrack \
--mem_mb 48000 \
--bold2t1w-dof 9 --dummy-scans 6 \
--use-aroma  --fd-spike-threshold 0.9  --cifti-output 91k \
--fs-license-file /optnfs/freesurfer/6.0.0/license.txt \
# ${BIDS_DIRECTORY} ${OUTPUT_DIR} participant --participant_label ${PARTICIPANT_LABEL} -w ${OUTPUT_WORK}


echo "COMPLETING fmriprep ... COPYING over"

# cp ${SCRATCH_DIR} ${OUTPUT_DIR}
# TODO: do not copy over the work folder
# cp ${SCRATCH_WORK} ${OUTPUT_WORK}

echo "process complete"


