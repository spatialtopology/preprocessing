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
logging.basicConfig(filename='task-cue_vicarious.log',  # Log file path
                    filemode='w',            # Append mode ('w' for overwrite)
                    level=logging.INFO,     # Logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log message format

# Step 3: Create a logger object
logger = logging.getLogger('vicarious')

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
def is_equivalent(val1, val2, tolerance=1):
    return abs(val1 - val2) <= tolerance
# TODO:

bids_dir = '/Users/h/Documents/projects_local/1076_spacetop' # the top directory of datalad
code_dir = '/Users/h/Documents/projects_local/1076_spacetop/code' # where this code live
source_dir = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata'# where the source behavioral directory lives
beh_inputdir = join(source_dir, 'd_beh')

# %% -----------------------------------------------
#                       cognitive
# -------------------------------------------------

task_name = 'vicarious'
cognitive_flist = glob.glob(join(beh_inputdir,'sub-*', '**','task-social', '**', f'*{task_name}*.csv'), recursive=True)
filtered_cognitive_flist = [file for file in cognitive_flist if "sub-0001" not in file]
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
for cognitive_fpath in sorted(filtered_cognitive_flist):
# %%
    # 1. create an empty dataframe to host new BIDS data _______________________
    bids_beh = pd.DataFrame(columns=['onset', 'duration', 'trial_type','trial_index','cue', 'stimulusintensity', 'rating_value', 'rating_glmslabel', 'rating_value_fillna', 'rating_glmslabel_fillna','rating_mouseonset','rating_mousedur','stim_file'])
    cue = bids_beh.copy();
    expect = bids_beh.copy();
    stim = bids_beh.copy();
    outcome = bids_beh.copy();
    logger.info(f"\n\n{cognitive_fpath}")   
    # 2. extract metadata from original behavioral file ________________________
    cognitive_fname = os.path.basename(cognitive_fpath)
    sub_bids = re.search(r'sub-\d+', cognitive_fname).group(0)
    ses_bids = re.search(r'ses-\d+', cognitive_fname).group(0)
    run_bids = re.search(r'run-\d+', cognitive_fname).group(0)
    runtype = re.search(r'run-\d+-(\w+?)_', cognitive_fname).group(1)


    logger.info(f"_______ {sub_bids} {ses_bids} {run_bids} {runtype} _______")
    beh_savedir = join(bids_dir, sub_bids, ses_bids, 'func')
    beh_df = pd.read_csv(cognitive_fpath)
    trigger = beh_df['param_trigger_onset'][0]

    # 3. load trajectory data and calculate ratings ____________________________
    trajectory_glob = glob.glob(join(beh_inputdir, sub_bids, 'task-cue', ses_bids, f"{sub_bids}_{ses_bids}_task-cue_{run_bids}_runtype-{runtype}_beh-preproc.csv"))
    
    # if trajectory_glob:
    #     trajectory_fname = trajectory_glob[0]
    #     traj_df = pd.read_csv(trajectory_fname)
    # elif not trajectory_glob:
    #     logger.critical("Trajectory preproc is empty.")
    #     break
    try:
        if trajectory_glob:
            trajectory_fname = trajectory_glob[0]
            traj_df = pd.read_csv(trajectory_fname)
        else:
            # If trajectory_glob is empty, raise a custom exception
            raise FileNotFoundError("Trajectory preproc is empty.")
            
    except FileNotFoundError as e:
        logger.warning(str(e))
        continue 
    except Exception as e:
        # This catches any other exceptions that might occur
        logger.error("An error occurred while processing the trajectory file: %s", str(e))
        continue


    # 3-1. calculate degree based on x, y coordinate
    # Translate the points so that the reference point becomes the origin
    traj_df['expect_translated_x'] = traj_df['expectrating_end_x'] - trajectory_x
    traj_df['expect_translated_y'] = traj_df['expectrating_end_y'] - trajectory_y
    traj_df['outcome_translated_x'] = traj_df['outcomerating_end_x'] - trajectory_x
    traj_df['outcome_translated_y'] = traj_df['outcomerating_end_y'] - trajectory_y


    # 3-2. Calculate the angle in radians and then convert to degrees 
    traj_df['expectangle_degrees'] = np.degrees(np.arctan2(traj_df['expect_translated_y'], traj_df['expect_translated_x']))
    traj_df['outcomeangle_degrees'] = np.degrees(np.arctan2(traj_df['outcome_translated_y'], traj_df['outcome_translated_x']))

    traj_df['adjusted_expectangle_degrees'] = traj_df['expectangle_degrees'] % 180
    traj_df['adjusted_outcomeangle_degrees'] = traj_df['outcomeangle_degrees'] % 180


    # 3-3. check if the calculated new degree matches the one in beh_df

    beh_df['event02_expect_fillna'] = beh_df['event02_expect_angle'].round(2)
    beh_df['event02_expect_fillna'].fillna(traj_df['adjusted_expectangle_degrees'].round(2), inplace=True)
    comparison_series = beh_df['event02_expect_fillna'].round(2) == traj_df['adjusted_expectangle_degrees'].round(2)
    traj_df['comparison_flag'] = ~comparison_series
    expect_overall_flag = traj_df['comparison_flag'].any()
    if expect_overall_flag:
        discrepancy_indices = traj_df[traj_df['comparison_flag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tExpect Rating {idx}: (traj_df): {traj_df.loc[idx]['adjusted_expectangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event02_expect_fillna']}")

    beh_df['event04_outcome_fillna'] = beh_df['event04_actual_angle'].round(2)
    beh_df['event04_outcome_fillna'].fillna(traj_df['adjusted_outcomeangle_degrees'].round(2), inplace=True)
    outcome_comparison_mask = beh_df['event04_actual_angle'].round(2) == traj_df['adjusted_outcomeangle_degrees'].round(2)
    traj_df['outcome_comparisonflag'] = ~outcome_comparison_mask
    outcome_overall_flag = traj_df['outcome_comparisonflag'].any()

    if outcome_overall_flag:
        discrepancy_indices = traj_df[traj_df['outcome_comparisonflag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tOutcome Rating {idx} (traj_df): {traj_df.loc[idx]['adjusted_outcomeangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event04_outcome_fillna']}")



        # break


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
    cue['stim_file'] = beh_df["event01_cue_filename"]


          
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
    expect['stim_file'] = beh_df["event01_cue_filename"]

    
    # 6. stim __________________________________________________________________

    stim['onset'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
    stim['duration'] = (beh_df['ISI03_onset'] - beh_df['event03_stimulus_displayonset']).round(2)
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
    stim['stim_file'] = beh_df['event03_C_stim_filename'] 
    stim['accuracy'] = beh_df['event03_C_stim_match'].map({'same':, 'diff':}) (same, diff) 
    stim['event03_stimulusC_responsekeyname'] (right, left)


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
    outcome['stim_file'] = 'task-vicarious_scale.png'


    events = pd.concat([cue, expect, stim, outcome], ignore_index=True)
    events_sorted = events.sort_values(by='onset')

    if os.path.exists(beh_savedir) and os.path.isdir(beh_savedir):
        events.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-{task_name}_{run_bids}_events.tsv"), sep='\t', index=False)
    else:
        logger.critical(f"WARNING: The directory {beh_savedir} does not exist.")
    
    # extract bids info and save as new file

# %%
