# split runs with "trigger event" e.g. binarize the values and identify start stop indices
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

# %% directories ___________________________________
# current_dir = os.getcwd()
# main_dir = Path(current_dir).parents[1]

# %% temporary
main_dir = '/Volumes/spacetop'
print(main_dir)
save_dir = os.path.join(main_dir, 'biopac', 'dartmouth', 'b03_extract_ttl')
print(save_dir)
# %% filename __________________________
# filename ='/Users/h/Dropbox/projects_dropbox/spacetop_biopac/data/sub-0026/SOCIAL_spacetop_sub-0026_ses-01_task-social_ANISO.acq'
acq_list = glob.glob(os.path.join(main_dir, 'biopac', 'dartmouth', 'b02_sorted', 'sub-' + ('[0-9]' * 4), '*', '*task-social*_ANISO.acq'), recursive = True)
flaglist = []
# %%
for acq in acq_list:
    filename  = os.path.basename(acq)
    sub = [match for match in filename.split('_') if "sub" in match][0]
    ses = [match for match in filename.split('_') if "ses" in match][0] # 'ses-03'
    task = [match for match in filename.split('_') if "task" in match][0]
    try: 
        spacetop_data, spacetop_samplingrate = nk.read_acqknowledge(acq)


        # %% EV trigger :: identify transitions based on "trigger" ev 
        mid_val = (np.max(spacetop_data['trigger']) - np.min(spacetop_data['trigger']))/2
        spacetop_data.loc[spacetop_data['trigger'] > mid_val, 'fmri_trigger'] = 5
        spacetop_data.loc[spacetop_data['trigger'] <= mid_val, 'fmri_trigger'] = 0

        start_df = spacetop_data[spacetop_data['fmri_trigger'] > spacetop_data[ 'fmri_trigger'].shift(1)].index
        stop_df = spacetop_data[spacetop_data['fmri_trigger'] < spacetop_data[ 'fmri_trigger'].shift(1)].index

        # %% EV TTL :: identify ttl events based on TTL column
        mid_val = (np.max(spacetop_data['TSA2 TTL - CBLCFMA - Current Feedback M']) - np.min(spacetop_data['TSA2 TTL - CBLCFMA - Current Feedback M']))/2
        spacetop_data.loc[spacetop_data['TSA2 TTL - CBLCFMA - Current Feedback M'] > mid_val, 'TTL'] = 5
        spacetop_data.loc[spacetop_data['TSA2 TTL - CBLCFMA - Current Feedback M'] <= mid_val, 'TTL'] = 0

        # %% EV stimuli :: 
        mid_val = (np.max(spacetop_data['administer']) - np.min(spacetop_data['administer']))/2
        spacetop_data.loc[spacetop_data['administer'] > mid_val, 'stimuli'] = 5
        spacetop_data.loc[spacetop_data['administer'] <= mid_val, 'stimuli'] = 0

        df_transition = pd.DataFrame({
                        'start_df': start_df, 
                        'stop_df': stop_df
                        })

        # identify runs with TTL signal
        ttl_bool = []
        for r in range(len(start_df)):
            bool_val = np.unique(spacetop_data.iloc[df_transition.start_df[r]:df_transition.stop_df[r],spacetop_data.columns.get_loc('TTL')]).any()
            ttl_bool.append(bool_val)

        runs_with_ttl = [i for i, x in enumerate(ttl_bool) if x]


    # %%    # FOR LOOP START _________________
        run_len = len(df_transition)
        if run_len == 6:
            for i, run_num in enumerate(runs_with_ttl):
                print(i, run_num)

                run = f"run-{run_num + 1:02d}"
                print(run)

                run_subset = spacetop_data[df_transition.start_df[run_num]: df_transition.stop_df[run_num]]
                run_df = run_subset.reset_index()
                # identify events :: expect and actual _________________
                start_expect = run_df[run_df['expect'] > run_df[ 'expect'].shift(1)]
                start_actual = run_df[run_df['actual'] > run_df[ 'actual'].shift(1)]
                stop_actual= run_df[run_df['actual'] < run_df[ 'actual'].shift(1)]

                # identify events :: stimulli _________________
                start_stim = run_df[run_df['stimuli'] > run_df[ 'stimuli'].shift(1)]
                stop_stim= run_df[run_df['stimuli'] < run_df[ 'stimuli'].shift(1)]
                events = nk.events_create(event_onsets=list(start_stim.index), 
                event_durations = list((stop_stim.index-start_stim.index)/spacetop_samplingrate))

                # transform events :: transform to onset _________________
                expect_start = start_expect.index/spacetop_samplingrate
                actual_end = stop_actual.index/spacetop_samplingrate
                stim_start = start_stim.index/spacetop_samplingrate
                stim_end = stop_stim.index/spacetop_samplingrate
                stim_onset = events['onset']/spacetop_samplingrate

                # build pandas dataframe _________________
                df_onset = pd.DataFrame({
                    'expect_start': expect_start, 
                    'actual_end': actual_end,
                    'stim_start': np.nan,
                    'stim_end':np.nan
                })

                df_stim = pd.DataFrame({
                    'stim_start': stim_start, 
                    'stim_end': stim_end
                    })

                final_df = pd.DataFrame()

                
                # events :: stimuli
                # for loop, identify the order of "stimulus events" 
                # based on information of "expect, actual" events, we will assign a trial number to stimulus events
                # RESOURCE: https://stackoverflow.com/questions/62300474/filter-all-rows-in-a-pandas-dataframe-where-a-given-value-is-between-two-columnv
                for i in range(len(df_stim)):
                    idx = pd.IntervalIndex.from_arrays(
                        df_onset['expect_start'], df_onset['actual_end'])
                    start_val = df_stim.iloc[i][df_stim.columns.get_loc('stim_start')]
                    interval_idx = df_onset[idx.contains(start_val)].index[0]
                    df_onset.iloc[interval_idx, df_onset.columns.get_loc('stim_start')] = start_val

                    end_val = df_stim.iloc[i][df_stim.columns.get_loc('stim_end')]
                    interval_idx = df_onset[idx.contains(end_val)].index[0]
                    df_onset.iloc[interval_idx, df_onset.columns.get_loc('stim_end')] = end_val
                    print(f"this is the {i}-th iteration. stim value is {start_val}, and is in between index {interval_idx}")

                # identify events :: TTL _________________
                # calculate TTL onsets
                start_ttl = run_df[run_df['TTL'] > run_df[ 'TTL'].shift(1)]
                stop_ttl = run_df[run_df['TTL'] < run_df[ 'TTL'].shift(1)]
                ttl_onsets =   list(start_ttl.index + (stop_ttl.index-start_ttl.index)/2)/spacetop_samplingrate
                print(f"ttl onsets: {ttl_onsets}, length of ttl onset is : {len(ttl_onsets)}")

                # define empty TTL data frame
                df_ttl = pd.DataFrame(np.nan, 
                                    index=np.arange(len(df_onset)),
                                    columns= ['ttl_1', 'ttl_2','ttl_3', 'ttl_4'])

                # identify which set of TTLs fall between expect and actual 
                pad = 1 # seconds. you may increase the value to have a bigger event search interval
                df_onset['expect_start_interval'] = df_onset['expect_start']-pad
                df_onset['actual_end_interval'] = df_onset['actual_end']+pad
                idx = pd.IntervalIndex.from_arrays(
                            df_onset['expect_start_interval'], df_onset['actual_end_interval'])

                for i in range(len(ttl_onsets)):
                    
                    val = ttl_onsets[i]
                    print(f"{i}-th value: {val}")
                    empty_cols = []
                    interval_idx = df_onset[idx.contains(val)].index[0]
                    print(f"\t\t* interval index: {interval_idx}")
                    mask = df_ttl.loc[[interval_idx]].isnull()
                    empty_cols = list(itertools.compress(np.array(df_ttl.columns.to_list()), mask.values[0]))
                    print(f"\t\t* empty columns: {empty_cols}")
                    df_ttl.loc[df_ttl.index[interval_idx], str(empty_cols[0])] = val
                    print(f"\t\t* this is the row where the value -- {val} -- falls. on the {interval_idx}-th row")


                # merge :: merge df_onset and df_ttl -> final output: final_df
                final_df = pd.merge(df_onset, df_ttl, left_index=True, right_index=True)
                final_df['ttl_r1'] = final_df['ttl_1'] - final_df['stim_start']
                final_df['ttl_r2'] = final_df['ttl_2'] - final_df['stim_start']
                final_df['ttl_r3'] = final_df['ttl_3'] - final_df['stim_start']
                final_df['ttl_r4'] = final_df['ttl_4'] - final_df['stim_start']

                # save output as
                save_filename = f"{sub}_{ses}_{task}_{run}_physio-ttl.csv"
                new_dir = os.path.join(save_dir, sub, ses, task)
                Path(new_dir).mkdir( parents=True, exist_ok=True )
                final_df.reset_index(inplace=True)
                final_df = final_df.rename(columns = {'index':'trial_num'})
                final_df.to_csv(os.path.join(new_dir, save_filename), index=False)

        else:
            flaglist.append(acq_list)

    except:
        flaglist.append(acq_list)

txt_filename = os.path.join(save_dir, 'biopac_flaglist.txt')
with open(txt_filename, 'w') as f:
    f.write(json.dumps(flaglist))


