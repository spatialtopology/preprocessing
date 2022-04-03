#!/usr/bin/env python3
"""
# split runs with "fMRI trigger" e.g. binarize the values and identify start stop indices
# ttl onsets
#   convert each event into trial number
# do this based on two events: expect and actual

# TODO:
# * identify BIDS scheme for physio data
# * flag files without ANISO
# * flag files with less than 5 runs
# ** for those runs, we need to manually assign run numbers (biopac will collect back to back)
# * change main_dir directory when running on discovery
# TODO: create metadata, of folders and how columns were calculated
# * remove unnecessary print statements
#
"""

# %% libraries ________________________
import neurokit2 as nk
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
import os, glob, shutil, datetime
from pathlib import Path
import json
import re

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development" 

def binarize_channel(data, origin_col, new_col, threshold, binary_h, binary_l):
    """
    data: pandas dataframe. acquisition file
    origin_col: columns with raw signal
    new_col: new columns for saving binarized origin_col values in
    threshold: int. threshold for binarizing values within pandas column
    binary_h, binary_l: two numbers. e.g. 5, 0 or 1, 0

    """
    data.loc[data[origin_col] > threshold, new_col] = binary_h
    data.loc[data[origin_col] <= threshold, new_col] = binary_l


# %% directories ___________________________________
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[1]

# %% temporary
# main_dir = '/Volumes/spacetop'
# print(main_dir)
save_dir = os.path.join(main_dir, 'biopac', 'dartmouth', 'b03_extract_ttl')
print(save_dir)
# %% filename __________________________
# filename ='/Users/h/Dropbox/projects_dropbox/spacetop_biopac/data/sub-0026/SOCIAL_spacetop_sub-0026_ses-01_task-social_ANISO.acq'
acq_list = glob.glob(os.path.join(main_dir, 'biopac', 'dartmouth',
                                  'b02_sorted', 'sub-' + ('[0-9]' * 4), '*',
                                  '*task-social*_physio.acq'),
                     recursive=True)
flaglist = []
runmeta = pd.read_csv('/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social/data/spacetop_task-social_run-metadata.csv')
txt_filename = os.path.join(
    save_dir, f'biopac_flaglist_{datetime.date.today().isoformat()}.txt')
# with open(txt_filename, 'w') as f:
#     f.write(json.dumps(flaglist))
f = open(txt_filename, "w")
# print()
# %%
for acq in sorted(acq_list):
    acq_fname = os.path.basename(acq)
    sub = [match for match in acq_fname.split('_') if "sub" in match][0]
    ses = [match for match in acq_fname.split('_') if "ses" in match][0]  # 'ses-03'
    task = [match for match in acq_fname.split('_') if "task" in match][0]
    print(f"\n__________________{sub} {ses} {task}__________________", file = f)
    try:
        
        spacetop_data, spacetop_samplingrate = nk.read_acqknowledge(acq)
        # ____________________________________ identify run transitions ____________________________________
        spacetop_data['mr_aniso'] = spacetop_data['fMRI Trigger - CBLCFMA - Current Feedba'].rolling(window=3).mean()
        binarize_channel(spacetop_data,
                            origin_col='mr_aniso',
                            new_col='spike',
                            threshold=40,
                            binary_h=5,
                            binary_l=0)
        start_spike = spacetop_data[spacetop_data['spike'] > spacetop_data['spike'].shift(1)].index
        stop_spike = spacetop_data[spacetop_data['spike'] < spacetop_data['spike'].shift(1)].index
        print(f"number of spikes within experiment: {len(start_spike)}", file = f)
        spacetop_data['bin_spike'] = 0
        spacetop_data.loc[start_spike, 'bin_spike'] = 5
        # %% EV trigger :: identify transitions based on "trigger" ev 
        spacetop_data['mr_aniso_boxcar'] = spacetop_data['fMRI Trigger - CBLCFMA - Current Feedba'].rolling(window=2000).mean()
        mid_val = (np.max(spacetop_data['mr_aniso_boxcar']) -
                    np.min(spacetop_data['mr_aniso_boxcar'])) / 4
        binarize_channel(spacetop_data,
                            origin_col='mr_aniso_boxcar',
                            new_col='mr_boxcar',
                            threshold=mid_val,
                            binary_h=5,
                            binary_l=0)
        start_df = spacetop_data[spacetop_data['mr_boxcar'] > spacetop_data['mr_boxcar'].shift(1)].index
        stop_df = spacetop_data[spacetop_data['mr_boxcar'] < spacetop_data['mr_boxcar'].shift(1)].index
        print(f"start_df: {start_df}")
        print(f"stop_df: {stop_df}")
        print(len(start_df))

        # _____________ adjust one TR (remove it!)_____________
        sdf= spacetop_data.copy()
        sdf.loc[start_df, 'bin_spike'] = 0

        nstart_df = sdf[sdf['bin_spike'] > sdf['bin_spike'].shift(1)].index
        nstop_df = sdf[sdf['bin_spike'] < sdf['bin_spike'].shift(1)].index
        print(nstart_df)
        print(nstop_df)

        sdf['adjusted_boxcar'] = sdf['bin_spike'].rolling(window=2000).mean()
        mid_val = (np.max(sdf['adjusted_boxcar']) -
                    np.min(sdf['adjusted_boxcar'])) / 4
        binarize_channel(sdf,
                            origin_col='adjusted_boxcar',
                            new_col='adjust_run',
                            threshold=mid_val,
                            binary_h=5,
                            binary_l=0)
        astart_df = sdf[sdf['adjust_run'] > sdf['adjust_run'].shift(1)].index
        astop_df = sdf[sdf['adjust_run'] < sdf['adjust_run'].shift(1)].index
        print(f"adjusted start_df: {astart_df}")
        print(f"adjusted stop_df: {astop_df}")
        # sdf.loc[start_df[0]-2:start_df[0]+2, 'fMRI Trigger - CBLCFMA - Current Feedba'] = 0

        # %% EV TTL :: identify ttl events based on TTL column
        sdf['TTL'] = sdf['TSA2 TTL - CBLCFMA - Current Feedback M'].rolling(window=2000).mean()
        sdf.loc[sdf['TTL'] > 5, 'ttl_aniso'] = 5
        sdf.loc[sdf['TTL'] <= 5, 'ttl_aniso'] = 0

        # %% EV stimuli :: 
        mid_val = (np.max(sdf['administer']) - np.min(sdf['administer']))/2
        sdf.loc[sdf['administer'] > mid_val, 'stimuli'] = 5
        sdf.loc[sdf['administer'] <= mid_val, 'stimuli'] = 0

        df_transition = pd.DataFrame({
            'start_df': astart_df,
            'stop_df': astop_df
        })
        # TODO: if run smaller than 300s, drop and remove from pandas
        # POP item from start_df, stop_df
        # spacetop_data.at[start_df[r]:stop_df[r], 'run_num'] = r+1
        for r in range(len(astart_df)):
            if (astop_df[r] - astart_df[r]) / 2000 < 300:
                sdf.drop(sdf.index[astart_df[r]:astop_df[r]],
                                   axis=0,
                                   inplace=True)
                astart_df.pop(r)
                astop_df.pop(r)

        # identify runs with TTL signal
        ttl_bool = []; runs_with_ttl = []; new_meta_run_with_ttl = []
        for r in range(len(astart_df)):
            bool_val = np.unique(sdf.iloc[
                df_transition.start_df[r]:df_transition.stop_df[r],
                sdf.columns.get_loc('ttl_aniso')]).any()
            ttl_bool.append(bool_val)
            sdf.at[start_df[r]:stop_df[r], 'run_num'] = r+1

        acq_runs_with_ttl = [i for i, x in enumerate(ttl_bool) if x]
        print(f"acq_runs_with_ttl: {acq_runs_with_ttl}")

        # TODO: check if runs_with_ttl matches the index from the ./social_influence-analysis/data/spacetop_task-social_run-metadata.csv

        a = runmeta.loc[(runmeta['sub'] == sub) & (runmeta['ses'] == ses)]
        ttl_list_from_meta = a.columns[a.eq('pain').any()]
        meta_runs_with_ttl = [int(re.findall('\d+', s)[0])  for s in list(ttl_list_from_meta) ]
        new_meta_run_with_ttl[:] = [m - 1 for m in meta_runs_with_ttl]

        print(f"new_meta_run_with_ttl: {new_meta_run_with_ttl}")
        # ____________________________________ identify TTL signals and trials ____________________________________
        # run_len = len(df_transition)
        # if run_len == 6:
        if acq_runs_with_ttl == new_meta_run_with_ttl:
            
            print(f"runs with ttl: {acq_runs_with_ttl}", file = f)
            for i, run_num in enumerate(acq_runs_with_ttl):
                run_subset = spacetop_data.loc[spacetop_data['run_num'] ==
                                               run_num + 1]
                print(len(run_subset) / spacetop_samplingrate)
                if 300 < len(run_subset)/spacetop_samplingrate < 450:  # TODO: check if run length is around 389 s
                    print(i, run_num)

                    run = f"run-{run_num + 1:02d}"
                    print(run, file = f)

                    run_df = run_subset.reset_index()
                    # identify events :: expect and actual _________________
                    start_expect = run_df[
                        run_df['expect'] > run_df['expect'].shift(1)]
                    start_actual = run_df[
                        run_df['actual'] > run_df['actual'].shift(1)]
                    stop_actual = run_df[
                        run_df['actual'] < run_df['actual'].shift(1)]

                    # identify events :: stimulli _________________
                    start_stim = run_df[
                        run_df['stimuli'] > run_df['stimuli'].shift(1)]
                    stop_stim = run_df[
                        run_df['stimuli'] < run_df['stimuli'].shift(1)]
                    events = nk.events_create(
                        event_onsets=list(start_stim.index),
                        event_durations=list(
                            (stop_stim.index - start_stim.index) /
                            spacetop_samplingrate))

                    # transform events :: transform to onset _________________
                    expect_start = start_expect.index / spacetop_samplingrate
                    actual_end = stop_actual.index / spacetop_samplingrate
                    stim_start = start_stim.index / spacetop_samplingrate
                    stim_end = stop_stim.index / spacetop_samplingrate
                    stim_onset = events['onset'] / spacetop_samplingrate

                    # build pandas dataframe _________________
                    df_onset = pd.DataFrame({
                        'expect_start': expect_start,
                        'actual_end': actual_end,
                        'stim_start': np.nan,
                        'stim_end': np.nan
                    })

                    df_stim = pd.DataFrame({
                        'stim_start': stim_start,
                        'stim_end': stim_end
                    })
                    # ____________________________________ identify boundary conditions and assign TTL event to specific trial ____________________________________
                    # based on information of "expect, actual" events, we will assign a trial number to stimulus events
                    # RESOURCE: https://stackoverflow.com/questions/62300474/filter-all-rows-in-a-pandas-dataframe-where-a-given-value-is-between-two-columnv
                    for i in range(len(df_stim)):
                        idx = pd.IntervalIndex.from_arrays(
                            df_onset['expect_start'], df_onset['actual_end'])
                        start_val = df_stim.iloc[i][df_stim.columns.get_loc(
                            'stim_start')]
                        interval_idx = df_onset[idx.contains(
                            start_val)].index[0]
                        df_onset.iloc[
                            interval_idx,
                            df_onset.columns.get_loc('stim_start')] = start_val

                        end_val = df_stim.iloc[i][df_stim.columns.get_loc(
                            'stim_end')]
                        interval_idx = df_onset[idx.contains(end_val)].index[0]
                        df_onset.iloc[
                            interval_idx,
                            df_onset.columns.get_loc('stim_end')] = end_val
                        print(
                            f"this is the {i}-th iteration. stim value is {start_val}, and is in between index {interval_idx}"
                        )
                    start_ttl = run_df[
                        run_df['ttl_aniso'] > run_df['ttl_aniso'].shift(1)]
                    stop_ttl = run_df[
                        run_df['ttl_aniso'] < run_df['ttl_aniso'].shift(1)]
                    ttl_onsets = list(start_ttl.index +
                                      (stop_ttl.index - start_ttl.index) /
                                      2) / spacetop_samplingrate
                    # print(f"ttl onsets: {ttl_onsets}, length of ttl onset is : {len(ttl_onsets)}")
                    # define empty TTL data frame
                    df_ttl = pd.DataFrame(
                        np.nan,
                        index=np.arange(len(df_onset)),
                        columns=['ttl_1', 'ttl_2', 'ttl_3', 'ttl_4'])
                    # identify which set of TTLs fall between expect and actual
                    pad = 1  # seconds. you may increase the value to have a bigger event search interval
                    df_onset['expect_start_interval'] = df_onset[
                        'expect_start'] - pad
                    df_onset[
                        'actual_end_interval'] = df_onset['actual_end'] + pad
                    adjusted = df_onset['actual_end_interval']
                    adjusted.iloc[-1, :] = len(run_subset) / 2000
                    a_idx = pd.IntervalIndex.from_arrays(
                        df_onset['expect_start_interval'], adjusted)
                    for i in range(len(ttl_onsets)):
                        val = ttl_onsets[i]  #
                        print(f"{i}-th value: {val}")
                        empty_cols = []
                        interval_idx = df_onset[a_idx.contains(val)].index[
                            0]  #
                        print(f"\t\t* interval index: {interval_idx}")
                        mask = df_ttl.loc[[interval_idx]].isnull()
                        empty_cols = list(
                            itertools.compress(
                                np.array(df_ttl.columns.to_list()),
                                mask.values[0]))  #
                        print(f"\t\t* empty columns: {empty_cols}")
                        df_ttl.loc[df_ttl.index[interval_idx],
                                   str(empty_cols[0])] = val  #
                        print(
                            f"\t\t* this is the row where the value -- {val} -- falls. on the {interval_idx}-th row"
                        )

                    # fdf = pd.concat([df_onset, df_ttl],axis = 1)
                    fdf = pd.merge(df_onset,
                                   df_ttl,
                                   left_index=True,
                                   right_index=True)
                    fdf['ttl_r1'] = fdf['ttl_1'] - fdf['stim_start']
                    fdf['ttl_r2'] = fdf['ttl_2'] - fdf['stim_start']
                    fdf['ttl_r3'] = fdf['ttl_3'] - fdf['stim_start']
                    fdf['ttl_r4'] = fdf['ttl_4'] - fdf['stim_start']
                    save_filename = f"{sub}_{ses}_{task}_{run}_physio-ttl.csv"
                    new_dir = os.path.join(save_dir, task, sub, ses)
                    print(f"directory: {new_dir}", file = f)
                    Path(new_dir).mkdir(parents=True, exist_ok=True)
                    fdf.reset_index(inplace=True)
                    fdf = fdf.rename(columns={'index': 'trial_num'})
                    fdf.to_csv(os.path.join(new_dir, save_filename),
                               index=False)

                    print(f"[x] success :: saved to {new_dir}", file = f)
                else:
                    print(f'\nrun length is shorter than 380s or longer than 410s' ,file = f)
                    print(acq, file = f)
        else:
            print("\n[flag] no runs with TTL or ttl in acquisition file and ttl in metadata does not match", file = f)
            print(acq, file = f)
            print(f"acq_runs_with_ttl: {acq_runs_with_ttl}", file = f)
            print(f"new_meta_run_with_ttl: {new_meta_run_with_ttl}", file = f)
    except:
        print('\n[flag] failed to read acquisition file', file = f)
        print(acq, file = f)


# txt_filename = os.path.join(/scripts/flags', f'biopac_flaglist_{datetime.date.today().isoformat()}.txt')
# with open(txt_filename, 'w') as f:
#     f.write(json.dumps(flaglist))
f.close()