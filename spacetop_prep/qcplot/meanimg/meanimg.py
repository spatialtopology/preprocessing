# %%
# load library
import os
from nilearn import plotting
from nilearn import datasets
from nilearn import image
import matplotlib.pyplot as plt
from pathlib import Path
import itertools
# help -----
# https://stackoverflow.com/questions/64331987/removing-hiding-empty-subplots-in-matplotlib-when-plotting-a-flexible-grid
# https://neurostars.org/t/multi-subjects-figures-with-nilearn-plotting/6042
# %% parameters ________________________________________________________________________
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[1] # discovery: /dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social
fmriprep_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'

# sub_list = ['sub-0019'] #, 'sub-0019', 'sub-0020']
sub_list = next(os.walk(fmriprep_dir))[1]
sub_list[sub]
ses_list = [3] #,3,4]
run_list = [1,2,3,4,5,6]
# TODO: 
fig, axes = plt.subplots(nrows=9, ncols=6, figsize=(14, 20))
fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(14, 20))
# axes is a 2 dimensional numpy array
for i, (sub, ses, run) in enumerate(total_list):
    print( sub, ses, run)
# for ax in axes.flatten():
    # axes.flat[i]
    filename = f"{sub}_ses-{ses:02d}_task-social_acq-mb8_run-{run}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    fullpath = Path(os.path.join(fmriprep_dir, sub, f"ses-{ses:02d}", "func", filename))
    if fullpath.is_file():
        brain = image.load_img(fullpath)
        meanimg = image.mean_img(brain)
        # TODO: save mean image as nifti
        display = plotting.plot_anat(meanimg, axes=axes.flat[i], vmax = 300)
        display = plotting.plot_stat_map(meanimg, axes=axes.flat[i], vmax = 300)

# %% save the output figure with all the anatomical images
fig.savefig("task-social_desc-mean-img-per-run.png")
# %%
