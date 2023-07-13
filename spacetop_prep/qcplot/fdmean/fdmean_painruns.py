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
flist = sorted(glob.glob(join(fmriprep_dir, sub, '*', 'func', f'{sub}_*_task-social_acq-mb8_run-*_desc-confounds_timeseries.tsv'), recursive=True))
meandf = pd.DataFrame(columns=['sub', 'ses', 'run', 'fd_mean', 'dvars_mean'], index = range(len(flist)))
for ind, fpath in enumerate(sorted(flist)):
    # calculate mean and add BIDS information
    fmridf = pd.read_csv(fpath, sep = '\t')
    meandf.loc[ind,'fd_mean'] = fmridf["framewise_displacement"].mean(axis=0)
    meandf.loc[ind,'dvars_mean'] = fmridf["dvars"].mean(axis=0)
    match_sub = re.search(r"sub-(\d+)", fpath).group(1)
    match_ses = re.search(r"ses-(\d+)", fpath).group(1) 
    match_run = re.search(r"run-(\d+)", fpath).group(1) 
    meandf.loc[ind,'sub'] = f"sub-{match_sub}"
    meandf.loc[ind,'ses'] = f"ses-{match_ses}"
    meandf.loc[ind,'run'] = f"run-{int(match_run):02d}"
    
save_fname = join(save_dir, f"fdmean_{sub}.tsv")
meandf.to_csv(save_fname, sep='\t', index=False, header=True)