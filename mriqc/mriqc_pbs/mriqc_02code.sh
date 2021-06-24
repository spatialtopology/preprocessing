#!/bin/bash -l
#PBS -N mriqc_spacetop
#PBS -q default
#PBS -l nodes=1:ppn=16
#PBS -l walltime=12:00:00
#PBS -A DBIC
#PBS -t 15
#PBS -l mem=10gb

cd $PBS_O_WORKDIR

#echo "PBSARRAY: " ${PBS_ARRAYID}

CONTAINER_IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-0.14.2.sif
MAINDIR=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/test_yarik/spacetop
BIDS_DIRECTORY=${MAINDIR}/spacetop_heudiconv
OUTPUT_DIR=${MAINDIR}/mriqc
WORK_DIR=${MAINDIR}/mriqc/work
#PARTICIPANT_LABEL=${PBS_ARRAYID}
PARTICIPANT_LABEL="0015"
singularity run -B ${MAINDIR}:${MAINDIR} \
-B ${OUTPUT_DIR}/work:${OUTPUT_DIR}/work \
-B /optnfs/freesurfer:/optnfs/freesurfer \
${CONTAINER_IMAGE} \
${BIDS_DIRECTORY} \
${OUTPUT_DIR} \
-w ${WORK_DIR} \
participant --participant-label ${PARTICIPANT_LABEL} \
--n_procs 16 \
--mem_gb 8 \
--write-graph \
--correct-slice-timing \
--fft-spikes-detector \
--fd_thres 0.2 \
--ica \
 
