#!/bin/bash -l
#SBATCH --job-name=WASABI_boldmeans
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=100gb
#SBATCH --time=24:00:00
#SBATCH -o boldmeans_%A_%a.o
#SBATCH -e boldmeans_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
# Find out how many files are needed to process by running files= and examine the size with echo ${#files[@]}
#SBATCH --array=0-780
# Email notifications (comma-separated options: BEGIN,END,FAIL)
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=END

hostname
module load matlab/r2022a
# Set the path to the fmriprep directory
fmriprep_dir="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep"
files=("$fmriprep_dir"/sub-*/ses-*/func/*task-social_acq-mb8_run-*_space-MNI152*preproc_bold.nii.gz)

# Extract subject
subject=$(basename "${files[$SLURM_ARRAY_TASK_ID]}" | cut -d'-' -f2 | cut -d'_' -f1)
# Extract session
ses=$(basename "${files[$SLURM_ARRAY_TASK_ID]}" | cut -d'-' -f3 | cut -d'_' -f1)
# Extract task
task=$(basename "${files[$SLURM_ARRAY_TASK_ID]}" | cut -d'-' -f4 | cut -d'_' -f1)
# Extract run
run=$(basename "${files[$SLURM_ARRAY_TASK_ID]}" |  grep -oP "(?<=_run-)\d+(?=_)" | head -n1)

echo "Running $((SLURM_ARRAY_TASK_ID+1)) of ${#files[@]} files"
echo "Subject: $subject, Session: $ses, Task: $task, Run: $run"

# Define file to process
input_file=${files[$SLURM_ARRAY_TASK_ID]}
# Define output path for Tmean
mean_output="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/meanimg/sub-$subject/$(basename "${files[$SLURM_ARRAY_TASK_ID]%.nii.gz}")_mean.nii"
mkdir -p "$(dirname "$mean_output")"

export MATLAB_NUM_THREADS=1

matlab -nodisplay -r "addpath(genpath('//dartfs-hpc/rc/lab/C/CANlab/modules/spm12')); addpath(genpath('//dartfs-hpc/rc/lab/C/CANlab/labdata/projects/WASABI/software')); mean_fmridata('$input_file', '$mean_output'); exit;"

module unload matlab