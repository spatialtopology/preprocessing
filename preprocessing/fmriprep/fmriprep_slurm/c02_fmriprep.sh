#!/bin/sh
#SBATCH --job-name=fmriprep
#SBATCH --mail-user=heejung.jung@colorado.edu
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --qos normal
#SBATCH --output ./log/fmriprep%j.out
#SBATCH --error ./log/fmriprep.e%j
#SBATCH --nodes 1
#SBATCH -c 6
#SBATCH -t 20:00:00
#SBATCH --exclusive
export OMP_NUM_THREADS=6
SUBJ=${1}

#SBATCH --ntasks-per-node 20
# export PYTHONPATH=/usr/lib/python2.7/dist-packages/:$PYTHONPATH
# /work/ics/data/projects/snaglab/modules/poldracklab_fmriprep_1.1.2-2018-07-06-2b914267bdac.img
# /work/ics/data/projects/snaglab/modules/poldracklab_fmriprep_1.0.4-2018-01-16-8800301e1d5e.img
# SINGULARITYENV_HOME=/work/ics/data/projects/snaglab/Projects/POKER.05/
# --bind /curc:/curc \
# fmriprep_ver1.1.4-2018-08-06.img
MAINDIR=/projects/heju9108/conformity.01

IMAGE=/projects/heju9108/container/fmriprep-1.5.7.sif
SOURCEDIR=${MAINDIR}/data/fontBIDS
OUTDIR=${MAINDIR}/data/derivatives
WORKDIR=${OUTDIR}/fmriprep/work/
FSLICENSE=/projects/ics/software/freesurfer/5.3.0/license.txt

unset PYTHONPATH; singularity run ${IMAGE} \
${SOURCEDIR} ${OUTDIR} \
participant --participant_label ${SUBJ} \
--nthreads 3 --omp-nthreads 3 --mem-mb 48000 \
--use-aroma --write-graph --ignore fieldmaps --fs-license-file ${FSLICENSE} \
-w ${WORKDIR} \
--fs-no-reconall --write-graph --notrack --output-space {T1w,template,fsnative}
