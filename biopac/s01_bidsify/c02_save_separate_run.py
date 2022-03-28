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

# %% libraries ________________________
import neurokit2 as nk
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
import os, shutil, glob
from pathlib import Path
import json

# %% temporary
main_dir = '/Volumes/spacetop'
print(main_dir)
save_dir = os.path.join(main_dir, 'biopac', 'dartmouth', 'b04_finalbids')
print(save_dir)

# %%
# 1. glob acquisition files __________________________
# filename ='/Users/h/Dropbox/projects_dropbox/spacetop_biopac/data/sub-0026/SOCIAL_spacetop_sub-0026_ses-01_task-social_ANISO.acq'
acq_list = glob.glob(os.path.join(main_dir, 'biopac', 'dartmouth', 'b02_sorted', 'sub-' + ('[0-9]' * 4), '*', '*task-social*_ANISO.acq'), recursive = True)
flaglist = []

for acq in acq_list:
    # 2. extract information from filenames __________________________
    filename  = os.path.basename(acq)
    sub = [match for match in filename.split('_') if "sub" in match][0]
    ses = [match for match in filename.split('_') if "ses" in match][0] # 'ses-03'
    task = [match for match in filename.split('_') if "task" in match][0]

    entities = dict(
    match.split('-')
    for match in filename.split('_')
    if '-' in match
    )

    try: 
        spacetop_data, spacetop_samplingrate = nk.read_acqknowledge(acq)


        # %% 3. 3. from the "trigger" channel
        # 1) binarize signals
        mid_val = (np.max(spacetop_data['trigger']) - np.min(spacetop_data['trigger']))/2
        spacetop_data.loc[spacetop_data['trigger'] > mid_val, 'fmri_trigger'] = 5
        spacetop_data.loc[spacetop_data['trigger'] <= mid_val, 'fmri_trigger'] = 0

        # 2) identify transitions

        start_df = spacetop_data[spacetop_data['fmri_trigger'] > spacetop_data[ 'fmri_trigger'].shift(1)].index
        stop_df = spacetop_data[spacetop_data['fmri_trigger'] < spacetop_data[ 'fmri_trigger'].shift(1)].index
        for r in range(len(start_df)):
            run_df = spacetop_data.iloc[start_df[ r]:stop_df[ r]]
            run_basename = f'{sub}_{ses}_{task}_run-{r:02d}_recording-ppg-eda_physio.acq'
            run_dir = os.path.join(save_dir, task, sub, ses )
            Path(run_dir).mkdir( parents=True, exist_ok=True )
            run_df.to_csv(os.path.join(run_dir, run_basename), index = False)
    except:
        flaglist.append(acq_list)

