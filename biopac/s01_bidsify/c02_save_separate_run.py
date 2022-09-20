# TODO: MARCH 08
# pop. how to deal with short-irrelavant runs while saving the runs in corresponding number.
#
# 1. [x] glob acquisition files
# 2. [x] extract information from filenames
# 3. [x] from the "trigger" channel

# 1) binarize signals
# 2) convert dataframe to seconds, instead of 2000 sampling rate.
# 2) identify transitions
# 3) see if transition is longer than expected TR (e.g. 872 TRs for task-social individual run)
# 4. [x] save using bids naming convention

# What if
# 1) if the data is shorter than expected run -> most-likely ignore
# [x] 2) what if data is longer than expected (e.g. forgot to start and stop run)
#      fmri_trigger will handle this
# TODO:
# [ ] need to identify which run is a pain run, in order to use the TTL

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

pwd = os.getcwd()
main_dir = Path(pwd).parents[0]
sys.path.append(os.path.join(main_dir))
sys.path.insert(0, os.path.join(main_dir))
print(sys.path)
from utils import preprocess
import utils

# TODO:
operating = sys.argv[1] #'local' vs. 'discovery'
task = sys.argv[2] # 'task-social' 'task-fractional' 'task-alignvideos'
# %% TODO: TST remove after development
operating = 'local'  # 'discovery'
task = 'task-social'
if operating == 'discovery':
    spacetop_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social'
    biopac_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/biopac/'
    save_dir = join(biopac_dir, 'dartmouth', 'b04_finalbids')
elif operating == 'local':
    spacetop_dir = '/Volumes/spacetop_projects_social'
    biopac_dir = '/Volumes/spacetop/biopac'  # /biopac/dartmouth/b04_finalbids/task-social'
    save_dir = join(biopac_dir, 'dartmouth', 'b04_finalbids')  # /biopac/dartmouth/b04_finalbids/task-social'

print(spacetop_dir)
print(biopac_dir)
print(save_dir)

# %%
# 1. glob acquisition files __________________________
# filename ='/Users/h/Dropbox/projects_dropbox/spacetop_biopac/data/sub-0026/SOCIAL_spacetop_sub-0026_ses-01_task-social_ANISO.acq'
acq_list = glob.glob(os.path.join(biopac_dir,  "dartmouth", "b02_sorted", "**," "**", f"*{task}*.acq"),
                     recursive=True)
flaglist = []
runmeta = pd.read_csv(
    join(spacetop_dir, "data/spacetop_task-social_run-metadata.csv"))
txt_filename = os.path.join(
    save_dir, f"biopac_flaglist_{datetime.date.today().isoformat()}.txt")
# with open(txt_filename, 'w') as f:
f = open(txt_filename, "w")
# %%
for acq in sorted(acq_list):
    # 2. extract information from filenames __________________________
    filename = os.path.basename(acq)
    sub = [match for match in filename.split('_') if 'sub' in match][0]
    ses = [match for match in filename.split(
        '_') if 'ses' in match][0]  # 'ses-03'
    task = [match for match in filename.split('_') if 'task' in match][0]

    try:
        spacetop_data, spacetop_samplingrate = nk.read_acqknowledge(acq)

        #  3. 3. from the "trigger" channel
        # 1) binarize signals
        # mid_val = (np.max(spacetop_data['trigger']) - np.min(spacetop_data['trigger']))/2
        # spacetop_data.loc[spacetop_data['trigger'] > mid_val, 'fmri_trigger'] = 5
        # spacetop_data.loc[spacetop_data['trigger'] <= mid_val, 'fmri_trigger'] = 0
        # ____________________________________ identify run transitions ____________________________________
        spacetop_data['mr_aniso'] = spacetop_data['fMRI Trigger - CBLCFMA - Current Feedba'].rolling(
            window=3).mean()
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
        print(
            f"number of spikes within experiment: {len(start_spike)}", file=f)
        spacetop_data['bin_spike'] = 0
        spacetop_data.loc[start_spike, 'bin_spike'] = 5
        # TODO: deprecate 1) - use mri aniso to separate runs:
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
        print(f"start_df: {start_df}")
        print(f"stop_df: {stop_df}")
        print(f"total of {len(start_df)} runs")

        # _____________ adjust one TR (remove it!)_____________
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
        print(f"adjusted start_df: {astart_df}")
        print(f"adjusted stop_df: {astop_df}")

        # 2) identify transitions

        # start_df = spacetop_data[spacetop_data['fmri_trigger'] > spacetop_data[ 'fmri_trigger'].shift(1)].index
        # stop_df = spacetop_data[spacetop_data['fmri_trigger'] < spacetop_data[ 'fmri_trigger'].shift(1)].index

        # 3) if start_df and stop_df difference is greater than 300 seconds, include.
        # 4) if not, exclude from dataset
        # 5) pop run number
        run_list = list(range(len(astart_df)))
        run_bool = ((astop_df-astart_df)/spacetop_samplingrate) > 300
        clean_runlist = list(compress(run_list, run_bool))
        shorter_than_300 = list(compress(run_list, ~run_bool))
        if len(shorter_than_300) > 0:
            flaglist.append(
                f"runs shorter than 300 sec: {sub} {ses} {shorter_than_300} - run number in python order")

        for r in clean_runlist:
            run_df = spacetop_data.iloc[astart_df[r]:astop_df[r]]
            run_basename = f"{sub}_{ses}_{task}_run-{r+1:02d}_recording-ppg-eda_physio.acq"
            run_dir = os.path.join(save_dir, task, sub, ses)
            Path(run_dir).mkdir(parents=True, exist_ok=True)
            run_df.to_csv(os.path.join(run_dir, run_basename), index=False)
    except:
        flaglist.append(acq_list)
