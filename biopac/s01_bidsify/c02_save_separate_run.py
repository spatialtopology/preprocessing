#!/usr/bin/env python
""" Separates acq into runs and saves as bids format. 
This script reads the acquisition file collected straight from our biopac PC

Parameters
------------------
operating: str
    options: 'local' vs. 'discovery'
task: str
    options: 'task-social', 'task-fractional' 'task-alignvideos', 'task-faces', 'task-shortvideos'
cutoff_threshold: int
    threshold for determining "kosher" runs versus not. 
    for instance, task-social is 398 seconds long. I use the threshold of 300 as a threshold. 
    Anything shorter than that is discarded and not converted into a run

Steps (TODO coding)
------------------
1) [x] glob acquisitions files
2) [x] extract information from filesnames
3) [x] binarize signals based on MR Trigger channel (received RF pulse)
4) [x] convert dataframe to seconds, instead of 2000 sampling rate.
5) [x] identify transitions
6) [x] check if transition is longer than expected TR (threshold 300 s)
6-1) if longer than threshold, include and save as separate run
6-2) if less than expected, flag and keep a note in the flatlist. Pop that index using boolean mask. 
7) [x] save using bids naming convention

Questions: 
------------------
1) What if the data is shorter than expected run 
A: most-likely ignore

2) what if data is longer than expected (e.g. forgot to start and stop run)?
A: No worries, we're using the channel with the MRtriggers "fMRI Trigger - CBLCFMA - Current Feedba"
"""

# %% libraries ________________________
import neurokit2 as nk
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
import os
import sys
import shutil
import glob
from pathlib import Path
import json
from itertools import compress
import datetime
from os.path import join
import logging

pwd = os.getcwd()
main_dir = Path(pwd).parents[0]
sys.path.append(os.path.join(main_dir))
sys.path.insert(0, os.path.join(main_dir))
print(sys.path)

import utils
from utils import preprocess

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
# people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__credits__ = ["Heejung"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

# TODO:
operating = sys.argv[1]  # 'local' vs. 'discovery'
task = sys.argv[2]  # 'task-social' 'task-fractional' 'task-alignvideos'
cutoff_threshold = sys.argv[3]
# %% TODO: TST remove after development
#operating = 'local'  # 'discovery'
#task = 'task-social'
#cutoff_threshold = 300
print(f"operating: {operating}")
if operating == 'discovery':
    spacetop_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social'
    biopac_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/biopac/'
    save_dir = join(biopac_dir, 'dartmouth', 'b04_finalbids')

elif operating == 'local':
    spacetop_dir = '/Volumes/spacetop_projects_social'
    # /biopac/dartmouth/b04_finalbids/task-social'
    biopac_dir = '/Volumes/spacetop/biopac'
    # /biopac/dartmouth/b04_finalbids/task-social'
    save_dir = join(biopac_dir, 'dartmouth', 'b04_finalbids')

print(spacetop_dir)
print(biopac_dir)
print(save_dir)

# set up logger _______________________________________________________________________________________
flaglist = []
runmeta = pd.read_csv(
    join(spacetop_dir, "data/spacetop_task-social_run-metadata.csv"))
txt_filename = os.path.join(
    save_dir, f"biopac_flaglist_{task}_{datetime.date.today().isoformat()}.txt")
# with open(txt_filename, 'w') as f:
f = open(txt_filename, "w")

formatter = logging.Formatter("%(levelname)s - %(message)s")
handler = logging.FileHandler(txt_filename)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
logging.getLogger().addHandler(ch)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# %% 1. glob acquisition files ____________________________________________________________________________
# filename ='/Users/h/Dropbox/projects_dropbox/spacetop_biopac/data/sub-0026/SOCIAL_spacetop_sub-0026_ses-01_task-social_ANISO.acq'

biopac_list = next(os.walk(join(biopac_dir, 'dartmouth', 'b02_sorted')))[1]  
remove_int = [1, 2, 3, 4, 5, 6]
remove_list = [f"sub-{x:04d}" for x in remove_int]
sub_list = [x for x in biopac_list if x not in remove_list]
acq_list = []
print(sub_list)
for sub in sub_list:
    acq = glob.glob(os.path.join(biopac_dir,  "dartmouth", "b02_sorted", sub, "**", f"*{task}*.acq"),
                     recursive=True)
    acq_list.append(acq)

flat_acq_list = [item for sublist in acq_list  for item in sublist]
#print(flat_acq_list)
# %%
for acq in sorted(flat_acq_list):
    # extract information from filenames _______________________________________________________________
    filename = os.path.basename(acq)
    sub = [match for match in filename.split('_') if 'sub' in match][0]
    ses = [match for match in filename.split(
        '_') if 'ses' in match][0]  # 'ses-03'
    task = [match for match in filename.split('_') if 'task' in match][0]

    try:
        spacetop_data, spacetop_samplingrate = nk.read_acqknowledge(acq)
        logger.info(f"\n\n__________________{sub} {ses} __________________")
        logger.info(f"file exists! -- starting tranformation: ")
    except:
        logger.error(f"\n\n__________________{sub} {ses} __________________")
        logger.error(f"\tno biopac file exists")
        flaglist.append(acq_list)
       #: continue
    # identify run transitions _________________________________________________________________________
    try:
        spacetop_data['mr_aniso'] = spacetop_data['fMRI Trigger - CBLCFMA - Current Feedba'].rolling(
        window=3).mean()
    except:
        logger.info(f"\n\n__________________{sub} {ses} __________________")
        logger.error(f"\tno MR trigger channel - this was the early days. re run and use the *trigger channel*")
        flaglist.append(acq_list)
        continue
    utils.preprocess._binarize_channel(spacetop_data,
                                       source_col='mr_aniso',
                                       new_col='spike',
                                       threshold=40,
                                       binary_high=5,
                                       binary_low=0)
    start_spike = spacetop_data[spacetop_data['spike']
                                > spacetop_data['spike'].shift(1)].index
    stop_spike = spacetop_data[spacetop_data['spike']
                               < spacetop_data['spike'].shift(1)].index
    logger.info(f"number of spikes within experiment: {len(start_spike)}")
    spacetop_data['bin_spike'] = 0
    spacetop_data.loc[start_spike, 'bin_spike'] = 5
    # 2)
    spacetop_data['mr_aniso_boxcar'] = spacetop_data['fMRI Trigger - CBLCFMA - Current Feedba'].rolling(
        window=2000).mean()
    mid_val = (np.max(spacetop_data['mr_aniso_boxcar']) -
               np.min(spacetop_data['mr_aniso_boxcar'])) / 4
    utils.preprocess._binarize_channel(spacetop_data,
                                       source_col='mr_aniso_boxcar',
                                       new_col='mr_boxcar',
                                       threshold=mid_val,
                                       binary_high=5,
                                       binary_low=0)
    start_df = spacetop_data[spacetop_data['mr_boxcar']
                             > spacetop_data['mr_boxcar'].shift(1)].index
    stop_df = spacetop_data[spacetop_data['mr_boxcar']
                            < spacetop_data['mr_boxcar'].shift(1)].index
    print(f"* start_df: {start_df}")
    print(f"* stop_df: {stop_df}")
    print(f"* total of {len(start_df)} runs")

    # _____________ adjust one TR (remove it!)__________________________________________________________
    sdf = spacetop_data.copy()
    sdf.loc[start_df, 'bin_spike'] = 0

    nstart_df = sdf[sdf['bin_spike'] > sdf['bin_spike'].shift(1)].index
    nstop_df = sdf[sdf['bin_spike'] < sdf['bin_spike'].shift(1)].index
    print(nstart_df)
    print(nstop_df)

    sdf['adjusted_boxcar'] = sdf['bin_spike'].rolling(window=2000).mean()
    mid_val = (np.max(sdf['adjusted_boxcar']) -
               np.min(sdf['adjusted_boxcar'])) / 4
    utils.preprocess._binarize_channel(sdf,
                                       source_col='adjusted_boxcar',
                                       new_col='adjust_run',
                                       threshold=mid_val,
                                       binary_high=5,
                                       binary_low=0)
    astart_df = sdf[sdf['adjust_run'] > sdf['adjust_run'].shift(1)].index
    astop_df = sdf[sdf['adjust_run'] < sdf['adjust_run'].shift(1)].index
    print(f"* adjusted start_df: {astart_df}")
    print(f"* adjusted stop_df: {astop_df}")

    # 2) identify transitions
    run_list = list(range(len(astart_df)))
    run_bool = ((astop_df-astart_df)/spacetop_samplingrate) > 300
    clean_runlist = list(compress(run_list, run_bool))
    shorter_than_threshold_length = list(compress(run_list, ~run_bool))
    if len(shorter_than_threshold_length) > 0:
        flaglist.append(
            f"runs shorter than {cutoff_threshold} sec: {sub} {ses} {shorter_than_threshold_length} - run number in python order")

    for r in clean_runlist:
        run_df = spacetop_data.iloc[astart_df[r]:astop_df[r]]
        run_basename = f"{sub}_{ses}_{task}_run-{r+1:02d}_recording-ppg-eda_physio.acq"
        run_dir = os.path.join(save_dir, task, sub, ses)
        Path(run_dir).mkdir(parents=True, exist_ok=True)
        run_df.to_csv(os.path.join(run_dir, run_basename), index=False)


