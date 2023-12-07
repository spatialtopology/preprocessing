#!/bin/bash -l
#SBATCH --job-name=fdmean
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem-per-cpu=20G
#SBATCH --time=02:00:00
#SBATCH -o ./logplot/GLM_%A_%a.o
#SBATCH -e ./logplot/GLM_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=4%10

conda activate spacetop_env
echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep'
FMRIPREPDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'
OUTPUTDIR='/dartfs-hpc/scratch/f0042x1/tsnr'
#"/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/iqm"

python ${MAINDIR}\spacetop_prep/qcplot/iqmvalues/tsnr_spacetop.py \
--slurm-id ${ID} \
--fmriprepdir ${FMRIPREPDIR} \
--savedir ${OUTPUTDIR} \
--task "narratives"
