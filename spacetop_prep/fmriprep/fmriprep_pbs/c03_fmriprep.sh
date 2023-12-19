#!/bin/bash -l
#PBS -N fmriprep_cnfrm
#PBS -q default
#PBS -l nodes=1:ppn=8
#PBS -l walltime=20:00:00
#PBS -m bea

cd $PBS_O_WORKDIR
SUBJ=${1}

# PARAMETERS
IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep-20.0.5.sif
MAINDIR=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/conformity.01
BIDSDIR=${MAINDIR}/fontBIDS
OUTDIR=${MAINDIR}/derivatives
WORKDIR=${OUTDIR}/work/work-${SUBJ}

# GET DATA
module purge
module load freesurfer/6.0.0

# CONTAINER COMMAND
singularity run -B ${MAINDIR}:${MAINDIR} \
-B ${OUTDIR}/work:${OUTDIR}/work \
-B /optnfs/freesurfer:/optnfs/freesurfer ${IMAGE} \
--participant_label ${SUBJ} \
--write-graph \
--notrack \
--fs-no-reconall \
--use-aroma --nthreads 16 --omp-nthreads 16 \
--mem_mb 30000 \
--output-spaces MNI152NLin6Asym:res-2 MNI152NLin2009cAsym anat fsnative fsaverage5 \
--fs-license-file /optnfs/freesurfer/6.0.0/license.txt \
--fs-subjects-dir /fsdir \
${BIDSDIR} ${OUTDIR} participant -w ${WORKDIR}
