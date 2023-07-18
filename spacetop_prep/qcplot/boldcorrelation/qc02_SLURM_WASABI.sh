#!/bin/bash -l
#SBATCH --job-name=plot
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --mem-per-cpu=40G
#SBATCH --time=24:00:00
#SBATCH -o ./logplot/GLM_%A_%a.o
#SBATCH -e ./logplot/GLM_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-13%10

conda init
conda activate biopac
echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI'
NPYDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/numpy_bold'
OUTPUTDIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/fmriprep_bold_correlation"
#OUTPUTDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cue/figure/fmri/qc/fmriprep_bold_correlation'
# python ${MAINDIR}/scripts/biopac/wasabi-prep/spacetop_prep/qcplot/boldcorrelation/qc05_plotfmriprep.py \
python ${MAINDIR}/scripts/biopac/wasabi-prep/spacetop_prep/qcplot/boldcorrelation/qc02_fmriprepboldcorr.py \
--slurm-id ${ID} \
--inputdir ${NPYDIR} \
--outputdir ${OUTPUTDIR}
