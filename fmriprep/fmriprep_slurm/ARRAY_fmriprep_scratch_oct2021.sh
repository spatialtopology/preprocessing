#!/bin/bash -l
#SBATCH --job-name=fmriprep
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=03:00:00
#SBATCH -o ./log/FMRIPREP_%A_%a.o
#SBATCH -e ./log/FMRIPREP_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-2
## --array=1-17%5

#source /optnfs/common/miniconda3/etc/profile.d/conda.sh
#conda activate spacetop_env

# parameters _________________________________________________________
CONTAINER_IMAGE="/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep-20.2.3-LTS.sif"
MAINDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop"
#MAINDIR=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/temp_sfn
BIDS_DIRECTORY=${MAINDIR}/dartmouth
# BIDS_DIRECTORY="${MAINDIR}/temp_sfn"
SCRATCH_DIR="/dartfs-hpc/scratch/f0042x1/spacetop/preproc"
SCRATCH_WORK="${SCRATCH_DIR}/work"
OUTPUT_DIR="${MAINDIR}/derivatives/dartmouth/fmriprep"
OUTPUT_WORK="${OUTPUT_DIR}/work"
CODE_DIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/scripts/fmriprep/fmriprep_slurm"
#subjects=("0001" "0002" "0003" "0004" "0005"  "0007" "0008" "0009" "0010" \
#"0011" "0013" "0014" "0015" "0016" "0017" "0020")
# subjects=("0029" "0028" "0026" "0025" "0024" "0023" "0021" "0020" "0019" "0018" "0017" "0016" "0015" "0014" "0013" "0011")
subjects=("0053" "0055")
PARTICIPANT_LABEL=${subjects[$((SLURM_ARRAY_TASK_ID - 1 ))]}
echo "array id: " ${SLURM_ARRAY_TASK_ID}, "subject id: " ${PARTICIPANT_LABEL}

# mriqc command _________________________________________________________
echo $PYTHONPATH
unset $PYTHONPATH;
conda activate /dartfs-hpc/rc/home/1/f0042x1/.conda/envs/spacetop_env
# rm -rf .heudiconv .git/annex/transfer
# datalad clean

module purge
module load freesurfer/6.0.0
unset $PYTHONPATH;

singularity run --bind ${BIDS_DIRECTORY}:${BIDS_DIRECTORY} \
--bind ${SCRATCH_DIR}:${SCRATCH_DIR} \
--bind ${SCRATCH_WORK}:${SCRATCH_WORK}  \
--bind ${CODE_DIR}:${CODE_DIR} \
--bind /optnfs/freesurfer \
${CONTAINER_IMAGE} fmriprep \
${BIDS_DIRECTORY} ${SCRATCH_DIR} participant --participant_label ${PARTICIPANT_LABEL} -w ${SCRATCH_WORK} \
--task-id social \
--write-graph \
--n-cpus 8 \
--notrack \
--mem_mb 48000 \
--bold2t1w-dof 9 --dummy-scans 6 \
--fd-spike-threshold 0.9  \
--fs-no-reconall \
--fs-license-file /optnfs/freesurfer/6.0.0/license.txt \
# ${BIDS_DIRECTORY} ${OUTPUT_DIR} participant --participant_label ${PARTICIPANT_LABEL} -w ${OUTPUT_WORK}

echo "STARTING fmriprep ___________________________________________"
echo singularity exec --bind ${BIDS_DIRECTORY}:${BIDS_DIRECTORY} \
--bind ${SCRATCH_DIR}:${SCRATCH_DIR} \
--bind ${SCRATCH_WORK}:${SCRATCH_WORK}  \
--bind ${CODE_DIR}:${CODE_DIR} \
--bind /optnfs/freesurfer \
${CONTAINER_IMAGE}  fmriprep \
${BIDS_DIRECTORY} ${SCRATCH_DIR} participant --participant_label ${PARTICIPANT_LABEL} -w ${SCRATCH_WORK} \
--task-id social \
--write-graph \
--n-cpus 8 \
--notrack \
--mem_mb 48000 \
--bold2t1w-dof 9 --dummy-scans 6 \
--fd-spike-threshold 0.9  \
--fs-no-reconall \
--fs-license-file /optnfs/freesurfer/6.0.0/license.txt

echo "COMPLETING fmriprep ___________________________ COPYING over"
# if folder in CANlab exists, delete and then copy
SUB_FMRIPREP_DIR=${OUTPUT_DIR}/fmriprep/sub-${PARTICIPANT_LABEL}
rm -rf ${SUB_FMRIPREP_DIR}*
cp ${SCRATCH_DIR}/fmriprep/sub-${PARTICIPANT_LABEL}* ${OUTPUT_DIR}/fmriprep/
#cp ${SCRATCH_WORK} ${OUTPUT_WORK}

echo "_______________________ PROCESS COMPLETE ${PARTICIPANT_LABEL}"


