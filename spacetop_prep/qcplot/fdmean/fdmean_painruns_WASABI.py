#!/usr/bin/env python
"""
extract dvars and fd info from fmriprep_confounds_timeseries
calculate mean and append it with BIDS data
"""

__author__ = "Heejung Jung, Owen Collins"
__copyright__ = "Spatial Topology Project"
__credits__ = [""] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung.gr@dartmouth.edu"
__status__ = "Development" 
# ----------------------------------------------------------------------
#                               libraries
# ----------------------------------------------------------------------
import numpy as np
import pandas as pd
import os
import glob
from os.path import join
from pathlib import Path
import re
import argparse
# %% -------------------------------------------------------------------
#                               parameters 
# ----------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--slurm-id", 
                    type=int, help="slurm id in numbers")
parser.add_argument("--fmriprepdir", 
                    type=str, help="the top directory of fmriprep preprocessed files")
parser.add_argument("--savedir", 
                    type=str, help="the directory where you want to save your files")
args = parser.parse_args()
slurm_id = args.slurm_id
fmriprep_dir = args.fmriprepdir
save_dir = args.savedir

sub_folders = next(os.walk(fmriprep_dir))[1]
print(sub_folders)
sub_list = [i for i in sorted(sub_folders) if i.startswith('sub-')]
sub = sub_list[slurm_id]
# ----------------------------------------------------------------------
#                               main code
# ----------------------------------------------------------------------
# extract dvars and fd info from fmriprep_confounds_timeseries
# calculate mean and append it with BIDS data
flist = sorted(glob.glob(join(fmriprep_dir, sub, '*', 'func', f'{sub}_*_task-*_acq-mb8_run-*_desc-confounds_timeseries.tsv'), recursive=True))
meandf = pd.DataFrame(columns=['sub', 'ses', 'run', 'task', 'fd_mean', 'dvars_mean'], index = range(len(flist))) # Add a task column
for ind, fpath in enumerate(sorted(flist)):
    # add BIDS information
    match_sub = re.search(r"sub-(.*?)[\\/]", fpath).group(1) # Detect subjects encoded in various formats. 
    match_ses = re.search(r"ses-(\d+)", fpath).group(1) 
    match_run = re.search(r"run-(\d+)", fpath).group(1) 
    match_task = re.search(r"task-(.*?)[_]", fpath).group(1) # Add task name to the dataframe.
    
    meandf.loc[ind,'sub'] = f"sub-{match_sub}"
    meandf.loc[ind,'ses'] = f"ses-{match_ses}"
    meandf.loc[ind,'run'] = f"run-{int(match_run):02d}"
    meandf.loc[ind, 'task'] = f"task-{match_task}"  # Add task name to the dataframe.
    
    # Calculate mean
    # Check to ensure there's content in the file. Sometimes there is not.
    try:
        fmridf = pd.read_csv(fpath, sep='\t')
        meandf.loc[ind,'fd_mean'] = fmridf["framewise_displacement"].mean(axis=0)
        meandf.loc[ind,'dvars_mean'] = fmridf["dvars"].mean(axis=0)
    except pd.errors.EmptyDataError:
        # Handle the EmptyDataError here, for example, print an error message
        print(match_sub+"_"+match_ses+"_"+match_run+"_"+match_task+"_"+"Error: No columns to parse from file or the file is empty.")
        meandf.loc[ind, 'fd_mean'] = None
        meandf.loc[ind, 'dvars_mean'] = None
    
save_fname = join(save_dir, 'fdmean', f"fdmean_{sub}.tsv")
# Create the 'fdmean' directory if it doesn't exist
os.makedirs(os.path.dirname(save_fname), exist_ok=True)  # Generate directories that do not yet exist.
meandf.to_csv(save_fname, sep='\t', index=False, header=True)