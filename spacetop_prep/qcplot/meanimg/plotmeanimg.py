# %%
# load library
import os
from nilearn import plotting
from nilearn import datasets
from nilearn import image
import matplotlib.pyplot as plt
from pathlib import Path
import itertools
import sys, argparse
# help -----
# https://stackoverflow.com/questions/64331987/removing-hiding-empty-subplots-in-matplotlib-when-plotting-a-flexible-grid
# https://neurostars.org/t/multi-subjects-figures-with-nilearn-plotting/6042
# %% parameters ________________________________________________________________________
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[1] # discovery: /dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social
fmriprep_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'

# load image filename
# calculate mean image
parser = argparse.ArgumentParser()
parser.add_argument("--slurm-id", 
                    type=int, help="slurm id in numbers")
args = parser.parse_args()
slurm_id = args.slurm_id
# fmriprep_dir = '/Volumes/spacetop_data/derivatives/fmriprep/results/fmriprep'

sub_list = next(os.walk(fmriprep_dir))[1]
sub_list = list(sub_list[slurm_id])
print(sub_list)
# sub_list = next(os.walk(csv_dir))[1]
ses_list = [1,3,4] #,3,4]
run_list = [1,2,3,4,5,6]
total_list = list(itertools.product(sub_list, ses_list, run_list))
# cuts = np.arange(i,j,k)
# create a figure with multiple axes to plot each anatomical image
# %%
# TODO: 
# fig, axes = plt.subplots(nrows=9, ncols=6, figsize=(14, 20))
# fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(14, 20))
# axes is a 2 dimensional numpy array
for i, (sub, ses, run) in enumerate(total_list):
    save_dir = os.path.join( '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc',sub )
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    print( sub, ses, run, i)
# for ax in axes.flatten():
    # axes.flat[i]
    filename = f"{sub}_ses-{ses:02d}_task-social_acq-mb8_run-{run}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    fullpath = Path(os.path.join(fmriprep_dir, sub, f"ses-{ses:02d}", "func", filename))
    if fullpath.is_file():
        brain = image.load_img(fullpath)
        meanimg = image.mean_img(brain)
        # display = plotting.plot_anat(meanimg, axes=axes.flat[i], vmax = 300)
        # display = plotting.plot_stat_map(meanimg, axes=axes.flat[i], vmax = 300)
        display = plotting.plot_stat_map(meanimg, 
                                        #  figure = fig, axes=axes.flat[i], 
                                         title = f"Sub: {sub}, Ses: {ses}, Run: {run}", vmax=300)
        # display.add_contours(meanimg, filled=False, alpha=0.7, colors='r')
        display.savefig(os.path.join(save_dir, f"meanimg_{sub}_ses-{ses:02d}_run-{run:02d}.png"))
        print("plot")
