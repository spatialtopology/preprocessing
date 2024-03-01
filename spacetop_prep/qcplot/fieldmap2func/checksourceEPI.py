
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

epi01_fname = '/Users/h/Documents/projects_local/sandbox/sub-0133_ses-01_task-social_acq-mb8_run-06_bold.nii.gz'
# fmapepi_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/fmap/sub-0010_ses-03_acq-mb8_fmapid-auto00004_desc-epi_fieldmap.nii.gz'
epi01 = image.mean_img(image.load_img(epi01_fname))
coords = (-5, -6, -15)
fig, axes = plt.subplots(2, 1, figsize=(10, 20))
display = plotting.plot_anat(epi01, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: source ses-01 ", 
                            figure = fig, cut_coords=coords, axes=axes[0], draw_cross=False)
# display.add_overlay(func_ref, cmap="Reds", alpha = .5)

fmapepi_f04 = '/Users/h/Documents/projects_local/sandbox/sub-0133_ses-04_task-social_acq-mb8_run-06_bold.nii.gz'
# fmapepi_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/fmap/sub-0010_ses-03_acq-mb8_fmapid-auto00004_desc-epi_fieldmap.nii.gz'
epi_04 = image.mean_img(image.load_img(fmapepi_f04))

display = plotting.plot_anat(epi_04, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: source ses-04 ", 
                            figure = fig, cut_coords=coords, axes=axes[1], draw_cross=False)
# display.add_overlay(func_ref, cmap="Reds", alpha = .5)

# %%
epi01_fname = '/Users/h/Documents/projects_local/sandbox/sub-0131_ses-01_task-social_acq-mb8_run-06_bold.nii.gz'
# fmapepi_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/fmap/sub-0010_ses-03_acq-mb8_fmapid-auto00004_desc-epi_fieldmap.nii.gz'
epi01 = image.mean_img(image.load_img(epi01_fname))
coords = (-5, -6, -15)
fig, axes = plt.subplots(2, 1, figsize=(10, 20))
display = plotting.plot_anat(epi01, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: sub-0131 source ses-01 ", 
                            figure = fig, display_mode='mosaic', axes=axes[0], draw_cross=False)
# display.add_overlay(func_ref, cmap="Reds", alpha = .5)

epi_f04 = '/Users/h/Documents/projects_local/sandbox/sub-0131_ses-04_task-social_acq-mb8_run-06_bold.nii.gz'
# fmapepi_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0010/ses-03/fmap/sub-0010_ses-03_acq-mb8_fmapid-auto00004_desc-epi_fieldmap.nii.gz'
epi_04 = image.mean_img(image.load_img(epi_f04))
# cut_coords=coords,
display = plotting.plot_anat(epi_04, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"Overlay: sub-0131 source ses-04 ", 
                            figure = fig, display_mode='mosaic', cut_coords=10, axes=axes[1], draw_cross=False)
# display.add_overlay(func_ref, cmap="Reds", alpha = .5)

# %%
# sub-0016 task narratives
# -------------------------
epi01_fname = '/Users/h/Documents/projects_local/sandbox/source_epi/sub-0016_ses-02_task-narratives_acq-mb8_run-03_bold.nii.gz'
epi01 = image.mean_img(image.load_img(epi01_fname))
coords = (-5, -6, -15)
# fig, axes = plt.subplots(1, 1, figsize=(10, 20))
# display = plotting.plot_anat(epi01, cmap='Blues', alpha=0.9, 
#                             colorbar=False, black_bg=False, dim=False, title=f"Overlay: sub-0016 source task-narrative run-03 ", 
#                             figure=fig, display_mode='mosaic', cut_coords=10, axes=axes[0], draw_cross=False)
# display.add_overlay(func_ref, cmap="Reds", alpha = .5)
display = plotting.plot_anat(epi01, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"source: sub-0016 task-narrative run-03 ", 
                             cut_coords=coords, draw_cross=False)

# %%
# sub-0010 task social
# -------------------------

coords = (-5, -6, -15)
fig, axes = plt.subplots(2, 1, figsize=(10, 20))

source_fname = '/Users/h/Documents/projects_local/sandbox/source_epi/sub-0010_ses-01_task-social_acq-mb8_run-03_bold.nii.gz'
source = image.mean_img(image.load_img(source_fname))
display = plotting.plot_anat(source, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"source: sub-0010 task-social run-03 ", 
                             cut_coords=coords, draw_cross=False)

fmriprep_fname = '/Users/h/Documents/projects_local/sandbox/source_epi/sub-0010_ses-01_task-social_acq-mb8_run-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
fmriprep = image.mean_img(image.load_img(fmriprep_fname))
display = plotting.plot_anat(fmriprep, cmap='Blues', alpha=0.9, 
                            colorbar=False, black_bg=False, dim=False, title=f"fmriprep: sub-0010 task-social run-03 ", 
                             cut_coords=coords, draw_cross=False)

