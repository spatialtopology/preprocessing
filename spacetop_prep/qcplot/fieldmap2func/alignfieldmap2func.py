# %% libraries
import os, glob, re
import shutil
import gzip
from os.path import join
from nilearn import image, plotting, masking
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools
import pathlib
import argparse

# %%

# load fieldmap _____________________________________________________
fmapepi_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/fmap/sub-0010_ses-03_acq-mb8_fmapid-auto00004_desc-epi_fieldmap.nii.gz'
fmap_epi = image.load_img(fmapepi_fname)
# load fieldmap _____________________________________________________
fmappreproc_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/fmap/sub-0010_ses-03_acq-mb8_fmapid-auto00001_desc-preproc_fieldmap.nii.gz'
fmap_preproc = image.load_img(fmappreproc_fname)
# load corresponding functional (mean) _____________________________________________________
func_reffname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/func/sub-0010_ses-03_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_boldref.nii.gz'
func_ref = image.load_img(func_reffname)
# mask
canlab_dir = '/Users/h/Documents/MATLAB/CanlabCore'
sub = "sub-0010"
mask_fname = join(canlab_dir, 'CanlabCore/canlab_canonical_brains/Canonical_brains_surfaces/brainmask_canlab.nii')
mask_fname_gz = mask_fname + '.gz'
brain_mask = image.load_img(mask_fname_gz)

func_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/func/sub-0010_ses-03_task-social_acq-mb8_run-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
meanfunc = image.mean_img(func_fname) #image.load_img(ref_img_fname)
threshold = 0.5

# nifti_masker = nilearn.maskers.NiftiMasker(mask_img= masking.compute_epi_mask(image.load_img(mask_fname_gz), lower_cutoff=threshold, upper_cutoff=1.0),
#                             target_affine = ref_img.affine, target_shape = ref_img.shape, 
#                     memory_level=1) # memory="nilearn_cache",


# overlay _____________________________________________________

# %%
coords = (-5, -6, -15)
fig, axes = plt.subplots(4, 1, figsize=(10, 20))
display = plotting.plot_anat(fmap_epi, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: fmap-epi & bold-ref\n* fmap: {os.path.basename(fmapepi_fname)}\n* epi: {os.path.basename(func_reffname)}", 
                            figure = fig, cut_coords=coords, axes=axes[0], draw_cross=False)
display.add_overlay(func_ref, cmap="Reds", alpha = .5)

# fmap-preproc & func ref
display = plotting.plot_anat(fmap_preproc, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: fmap-preproc & bold-ref", 
                            figure = fig, cut_coords=coords, axes=axes[1], draw_cross=False)
display.add_overlay(func_ref, cmap="Reds", alpha = .5)

# fmap-epi & meanfunc
display = plotting.plot_anat(fmap_epi, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: fmap-epi &  & mean_img bold", 
                            figure = fig, cut_coords=coords, axes=axes[2], draw_cross=False)
display.add_overlay(meanfunc, cmap="Reds", alpha = .5)

# fmap-preproc & meanfunc
display = plotting.plot_anat(fmap_preproc, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: fmap-preproc & mean_img bold", 
                            figure = fig, cut_coords=coords, axes=axes[3], draw_cross=False)
display.add_overlay(meanfunc, cmap="Reds", alpha = .5)

# %%
# Load sub-0131 T1
plotting.plot_anat('/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0131_ses-01_acq-MPRAGEXp3X08mm_desc-preproc_T1w.nii.gz')
# %%
# load fieldmap _____________________________________________________
fmappreproc_131_s1= '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0131_ses-01_acq-mb8_fmapid-auto00000_desc-preproc_fieldmap.nii.gz'
fmap_preproc131_s1 = image.load_img(fmappreproc_131_s1)

fmappreproc_131_s4= '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0131_ses-01_acq-mb8_fmapid-auto00000_desc-preproc_fieldmap.nii.gz'
fmap_preproc131_s4 = image.load_img(fmappreproc_131_s4)

func_131_s1 = image.mean_img(image.load_img('/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0131_ses-01_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'))
func_131_s4 = image.mean_img(image.load_img('/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0131_ses-04_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'))
# %%
coords = (-5, -6, -15)
fig, axes = plt.subplots(2, 1, figsize=(10, 20))
display = plotting.plot_anat(fmap_preproc131_s1, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: fmap-preproc & mean_img bold", 
                            figure = fig, cut_coords=coords, axes=axes[0], draw_cross=False)
display.add_overlay(func_131_s1, cmap="Reds", alpha = .5)

display = plotting.plot_anat(fmap_preproc131_s4, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: fmap-preproc & mean_img bold", 
                            figure = fig, cut_coords=coords, axes=axes[1], draw_cross=False)
display.add_overlay(func_131_s4, cmap="Reds", alpha = .5)

# %%
