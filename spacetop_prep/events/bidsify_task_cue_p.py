#!/usr/bin/env python
"""convert behavioral file into event lists and singletrial format

- regressor of interest per task
- duration of epoch
- rating onset
- potential covariates?
"""
# %%
import numpy as np
import pandas as pd
import os, glob, re, json
from os.path import join
from pathlib import Path
import logging

# Step 2: Configure the logging system
logging.basicConfig(filename='task-cue_pain.log',  # Log file path
                    filemode='w',            # Append mode ('w' for overwrite)
                    level=logging.INFO,     # Logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log message format

# Step 3: Create a logger object
logger = logging.getLogger('ExampleLogger')

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development" 

def calculate_ttl_values(stimulus_times, ttl_row, beh_df):
    # Retrieve the stimulus type from beh_df for the current row
    stimulus_type = beh_df['event03_stimulus_type']
    times = stimulus_times[stimulus_type]

    # Calculate TTL values if they are NaN in ttl_df
    if pd.isna(ttl_row['TTL1']):
        ttl_row['TTL1'] = beh_df['event03_stimulus_displayonset']
    if pd.isna(ttl_row['TTL2']):
        ttl_row['TTL2'] = ttl_row['TTL1'] + times['rampup']
    if pd.isna(ttl_row['TTL3']):
        ttl_row['TTL3'] = ttl_row['TTL2'] + times['plateau']
    if pd.isna(ttl_row['TTL4']):
        ttl_row['TTL4'] = ttl_row['TTL3'] + times['rampdown']
    
    return ttl_row
# %%
# TODO:

bids_dir = '/Users/h/Documents/projects_local/1076_spacetop' # the top directory of datalad
code_dir = '/Users/h/Documents/projects_local/1076_spacetop/code' # where this code live
source_dir = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata'# where the source behavioral directory lives
beh_inputdir = join(source_dir, 'd_beh')

# %% -----------------------------------------------
#                       pain
# -------------------------------------------------

task_name = 'pain'
pain_flist = glob.glob(join(beh_inputdir, '**','task-social', '**', f'*{task_name}*.csv'), recursive=True)
filtered_pain_flist = [file for file in pain_flist if "sub-0001" not in file]
trajectory_x = 960
trajectory_y = 707

# gLMS scale labels for expectation and outcome ratings
bins = [0, 1, 3, 10, 29, 64, 98, 180]
labels = [
    "No sensation",
    "Barely detectable",
    "Weak",
    "Moderate",
    "Strong",
    "Very Strong",
    "Strongest sensation of any kind"
]

# %%
for pain_fpath in sorted(filtered_pain_flist):
# %%
    # 1. create an empty dataframe to host new BIDS data _______________________
    bids_beh = pd.DataFrame(columns=['onset', 'duration', 'trial_type','trial_index',
'cue', 'stimulusintensity',  
'rating_value', 'rating_glmslabel', 'rating_value_fillna', 'rating_glmslabel_fillna','rating_mouseonset','rating_mousedur',

'stim_file', 
                              'onset_ttl1', 'onset_ttl2','onset_ttl3','onset_ttl4', 'stimulus_delivery_success'])
    cue = bids_beh.copy();
    expect = bids_beh.copy();
    stim = bids_beh.copy();
    outcome = bids_beh.copy();
   
    # 2. extract metadata from original behavioral file ________________________
    pain_fname = os.path.basename(pain_fpath)
    sub_bids = re.search(r'sub-\d+', pain_fname).group(0)
    ses_bids = re.search(r'ses-\d+', pain_fname).group(0)
    run_bids = re.search(r'run-\d+', pain_fname).group(0)
    runtype = re.search(r'run-\d+-(\w+?)_beh', pain_fname).group(1)


    logger.info(f"\n\n_______ {sub_bids} {ses_bids} {run_bids} {runtype} _______")
    beh_savedir = join(bids_dir, sub_bids, ses_bids, 'func')
    beh_df = pd.read_csv(pain_fpath)
    trigger = beh_df['param_trigger_onset'][0]

    # 3. load trajectory data and calculate ratings ____________________________
    trajectory_glob = glob.glob(join(beh_inputdir, sub_bids, 'task-cue', ses_bids, f"{sub_bids}_{ses_bids}_task-cue_{run_bids}_runtype-{runtype}_beh-preproc.csv"))
    
    if trajectory_glob:
        trajectory_fname = trajectory_glob[0]
        traj_df = pd.read_csv(trajectory_fname)
    elif not trajectory_glob:
        logger.critical("Trajectory preproc is empty.")
        continue


    # 3-1. calculate degree based on x, y coordinate
    # Translate the points so that the reference point becomes the origin
    traj_df['expect_translated_x'] = traj_df['expectrating_end_x'] - trajectory_x
    traj_df['expect_translated_y'] = traj_df['expectrating_end_y'] - trajectory_y
    traj_df['outcome_translated_x'] = traj_df['outcomerating_end_x'] - trajectory_x
    traj_df['outcome_translated_y'] = traj_df['outcomerating_end_y'] - trajectory_y
    # 3-2. Calculate the angle in radians and then convert to degrees 
    traj_df['expectangle_degrees'] = np.degrees(np.arctan2(traj_df['expect_translated_y'], traj_df['expect_translated_x']))
    traj_df['adjusted_expectangle_degrees'] = traj_df['expectangle_degrees'].apply(lambda x: x + 180 if x < 0 else x)

    traj_df['outcomeangle_degrees'] = np.degrees(np.arctan2(traj_df['outcome_translated_y'], traj_df['outcome_translated_x']))
    traj_df['adjusted_outcomeangle_degrees'] = traj_df['outcomeangle_degrees'].apply(lambda x: x + 180 if x < 0 else x)


    # 3-3. check if the calculated new degree matches the one in beh_df

    beh_df['event02_expect_fillna'] = beh_df['event02_expect_angle']
    beh_df['event02_expect_fillna'].fillna(traj_df['adjusted_expectangle_degrees'], inplace=True)
    comparison_mask = np.isclose(beh_df['event02_expect_angle'], traj_df['adjusted_expectangle_degrees'], atol=1)
    traj_df['comparison_flag'] = ~comparison_mask
    expect_overall_flag = traj_df['comparison_flag'].any()
    if expect_overall_flag:
        logger.error(f"{sub_bids} {ses_bids} {run_bids} 3-3. angles do not match between behavioral data and trajectory data")
        logger.info(beh_df['event02_expect_angle'].head(), beh_df['adjusted_expectangle_degrees'].head())
        continue

    beh_df['event04_outcome_fillna'] = beh_df['event04_actual_angle']
    beh_df['event04_outcome_fillna'].fillna(traj_df['adjusted_outcomeangle_degrees'], inplace=True)
    outcome_comparison_mask = np.isclose(beh_df['event04_actual_angle'], traj_df['adjusted_outcomeangle_degrees'], atol=1)
    traj_df['outcome_comparisonflag'] = ~outcome_comparison_mask
    outcome_overall_flag = traj_df['outcome_comparisonflag'].any()
    if outcome_overall_flag:
         logger.warning("3-3. angles do not match between behavioral data and trajectory data")



    # grab the intersection raise warning if dont match
    
    # map it to new label
    # 4. cue ___________________________________________________________________
    cue['onset'] = (beh_df['event01_cue_onset'] - trigger).round(2)
    cue['duration'] = (beh_df['ISI01_onset'] - beh_df['event01_cue_onset']).round(2)
    cue['trial_type'] = 'cue'
    cue['trial_index'] = beh_df.index +1
    cue['rating_value'] = "n/a"
    cue['rating_glmslabel'] = "n/a"
    cue['rating_value_fillna'] = "n/a"
    cue['rating_glmslabel_fillna'] = "n/a"
    cue['rating_mouseonset'] = "n/a"
    cue['rating_mousedur'] = "n/a"
    if (beh_df['event01_cue_type'] == beh_df['param_cue_type']).all():
        cue['cue'] = beh_df['event01_cue_type'] 
    else:
        logger.error(f"4-1. cue parameter does not match")
        continue
    cue['stimulusintensity'] =  "n/a"
    cue['onset_ttl1'] =  "n/a"
    cue['onset_ttl2'] =  "n/a"
    cue['onset_ttl3'] =  "n/a"
    cue['onset_ttl4'] =  "n/a"
    cue['stim_file'] = beh_df["event01_cue_filename"]
    cue['stimulus_delivery_success'] = "n/a"

          
    # 5. expect ________________________________________________________________
    expect['onset'] = (beh_df['event02_expect_displayonset'] - trigger).round(2)
    expect['duration'] = (beh_df['event02_expect_RT']).round(2)
    expect['trial_type'] = 'expectrating'
    expect['trial_index'] =  beh_df.index +1

    expect['rating_value'] =  beh_df['event02_expect_angle'].round(2)
    expect['rating_glmslabel'] = pd.cut(expect['rating_value'], 
                                        bins=bins, labels=labels, right=True)
    expect['rating_value_fillna'] = (beh_df['event02_expect_fillna']).round(2)
    expect['rating_glmslabel_fillna'] = pd.cut(expect['rating_value_fillna'], 
                                               bins=bins, labels=labels, right=True)
    expect['rating_mouseonset'] = (traj_df['expect_motiononset']).round(2)
    expect['rating_mousedur'] = (traj_df['expect_motiondur']).round(2)
    expect['cue'] = beh_df['event01_cue_type'] # if same as param_cue_type
    expect['stimulusintensity'] =  "n/a"
    expect['onset_ttl1'] =  "n/a"
    expect['onset_ttl2'] =  "n/a"
    expect['onset_ttl3'] =  "n/a"
    expect['onset_ttl4'] =  "n/a"
    expect['stim_file'] = beh_df["event01_cue_filename"]
    expect['stimulus_delivery_success'] = "n/a"
    
    # 6. stim __________________________________________________________________
    # 6-1. if ttl tsv exists, load in TTL duration
    ttldir = '/Volumes/spacetop_projects_cue/data/fmri/fmri01_onset/onset02_SPM'

    ttl_glob = glob.glob(join(ttldir, sub_bids, ses_bids, 
                               f"{sub_bids}_{ses_bids}_task-cue_{run_bids}_runtype-{runtype}_events_ttl.tsv"), recursive=True)
    stimulus_times = {
    'low_stim': {'rampup': 3.502, 'plateau': 5.000, 'rampdown': 3.402},
    'med_stim': {'rampup': 3.758, 'plateau': 5.000, 'rampdown': 3.606},
    'high_stim': {'rampup': 4.008, 'plateau': 5.001, 'rampdown': 3.813}
}
    if ttl_glob:
        ttl_fname = ttl_glob[0]
        ttl_df = pd.read_csv(ttl_fname, sep='\t')
        # if ttl_df is missing Value in ttl4, add back in value
        for i, ttl_row in ttl_df.iterrows():
            ttl_df.loc[i] = calculate_ttl_values(stimulus_times, ttl_row, beh_df.loc[i])
    else:
        logger.info("TTL dataframe non existent.")

        beh_df['total_stimulus_time'] = beh_df['event03_stimulus_type'].apply(lambda x: sum(stimulus_times[x].values()))
    temperature_map = {
    'high_stim': '50c',
    'med_stim': '49c',
    'low_stim': '48c'
    }

    stim['onset'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
    if ttl_glob: 
        stim['duration'] = (ttl_df['TTL4'] - ttl_df['TTL1']).round(2)
    else:
        stim['duration'] = ((beh_df['event03_stimulus_displayonset']-trigger) + beh_df['total_stimulus_time']).round(2)
    stim['trial_type'] = 'stimulus'
    stim['trial_index'] =  beh_df.index +1
    stim['rating_value'] = "n/a" 
    stim['rating_glmslabel'] =  "n/a" 
    stim['rating_value_fillna'] = "n/a"
    stim['rating_glmslabel_fillna'] = "n/a"
    stim['rating_mouseonset'] = "n/a"
    stim['rating_mousedur'] = "n/a"
    stim['cue'] = beh_df['event01_cue_type'] # if same as param_cue_type
    stim['stimulusintensity'] =  beh_df['event03_stimulus_type']

    if ttl_glob:
        stim['onset_ttl1'] = (ttl_df['TTL1']).round(2)
        stim['onset_ttl2'] = (ttl_df['TTL2']).round(2)
        stim['onset_ttl3'] = (ttl_df['TTL3']).round(2)
        stim['onset_ttl4'] = (ttl_df['TTL4']).round(2)
    else:
        stim['onset_ttl1'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
        stim['onset_ttl2'] = (stim['onset_ttl1'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['rampup'])).round(2)
        stim['onset_ttl3'] = (stim['onset_ttl2'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['plateau'])).round(2)
        stim['onset_ttl4'] = (stim['onset_ttl3'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['rampdown'])).round(2)

    stim['stim_file'] = beh_df['event03_stimulus_type'].map(temperature_map) 
    stim['stimulus_delivery_success'] = beh_df['event03_stimulus_P_trigger'].apply(lambda x: "success" if x == "Command Recieved: TRIGGER_AND_Response: RESULT_OK" else "fail")


    # outcome __________________________________________________________________
    outcome['onset'] = (beh_df['event04_actual_displayonset'] - trigger).round(2)
    outcome['duration'] = beh_df['event04_actual_RT'].round(2)
    outcome['trial_type'] = 'outcomerating'
    outcome['trial_index'] =  beh_df.index +1
    outcome['rating_value'] =  (beh_df['event04_actual_angle']).round(2)
    outcome['rating_glmslabel'] = pd.cut(outcome['rating_value'], 
                                         bins=bins, labels=labels, right=True)
    outcome['rating_value_fillna'] = beh_df['event04_outcome_fillna']
    outcome['rating_glmslabel_fillna'] = pd.cut(outcome['rating_value_fillna'], 
                                                bins=bins, labels=labels, right=True)
    outcome['rating_mouseonset'] = (traj_df['outcome_motiononset']).round(2)
    outcome['rating_mousedur'] = (traj_df['outcome_motiondur']).round(2)

    outcome['cue'] = beh_df['event01_cue_type'] 
    outcome['stimulusintensity'] =  beh_df['event03_stimulus_type']
    outcome['onset_ttl1'] =  "n/a"
    outcome['onset_ttl2'] =  "n/a"
    outcome['onset_ttl3'] =  "n/a"
    outcome['onset_ttl4'] =  "n/a"
    outcome['stim_file'] = 'task-pain_scale.png'
    outcome['stimulus_delivery_success'] = beh_df['event03_stimulus_P_trigger'].apply(lambda x: "success" if x == "Command Recieved: TRIGGER_AND_Response: RESULT_OK" else "fail")

    events = pd.concat([cue, expect, stim, outcome], ignore_index=True)
    events_sorted = events.sort_values(by='onset')

    if os.path.exists(beh_savedir) and os.path.isdir(beh_savedir):
        events.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-{task_name}_{run_bids}_events.tsv"), sep='\t', index=False)
    else:
        logger.critical(f"WARNING: The directory {beh_savedir} does not exist.")
    
    # extract bids info and save as new file

# %%
