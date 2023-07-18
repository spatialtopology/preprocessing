#!/bin/bash -l
#SBATCH --job-name=plot
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=24:00:00
#SBATCH -o ./logplot/np_%A_%a.o
#SBATCH -e ./logplot/np_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
# Each array index should be a subject
#SBATCH --array=1-13%10

conda init
conda activate biopac
echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI'
FMRIPREPDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep'
OUTPUTDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/numpy_bold'
python ${MAINDIR}/scripts/biopac/wasabi-prep/spacetop_prep/qcplot/boldcorrelation/qc01_saveniinumpy.py \
--slurm-id ${ID} \
--fmriprepdir ${FMRIPREPDIR} \
--outputdir ${OUTPUTDIR}
