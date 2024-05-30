#!/usr/bin/env python
"""
1. Unlock scans_tsv and update it based on runtype metadata
2. Harmonize discrepancy between nifti and behavioral data
3. Starting from Line 242, Behavioral data conversion to BIDS valid format
Same format occurs for pain, vicarious, cognitive data
convert behavioral file into event lists and singletrial format

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
import subprocess


__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development" 


# %% ---------------------------------------------------------------------------
#                                   Functions
# ------------------------------------------------------------------------------

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed with error: {result.stderr}")
    else:
        print(result.stdout)


def list_nifti_and_event_files(designated_dir):
    nifti_files = []
    event_files = []
    files = glob.glob(os.path.join(designated_dir, '**'), recursive=True)
    
    for file in files:
        if 'task-social' in file and file.endswith('.nii.gz'):
            nifti_files.append(file)
        elif 'task-cue' in file and file.endswith('_events.tsv'):
            event_files.append(file)

    return sorted(nifti_files), sorted(event_files)


def extract_run_and_task(filename):
    match = re.search(r'task-([a-zA-Z0-9]+)_.*_run-([0-9]+)', filename)
    if match:
        return match.groups()
    return None, None

def remove_orphan_nifti_files(nifti_files, event_files):
    event_file_basenames = [os.path.basename(f) for f in event_files]
    orphan_files = []

    for nifti_file in nifti_files:
        nifti_basename = os.path.basename(nifti_file)
        task, run = extract_run_and_task(nifti_basename)
        if task and run:
            expected_event_filename = f'sub-*_ses-*_task-cue*_run-{run}_desc*_events.tsv'
            if not any(re.match(expected_event_filename.replace('*', '.*'), event_filename) for event_filename in event_file_basenames):
                orphan_files.append(nifti_file)
    
    return orphan_files


def extract_cue_metadata_and_run(filename):
    cue_metadata = re.search(r'_desc-(\w+)_events\.tsv', filename).group(1)
    run = re.search(r'_run-(\d+)_', filename).group(1)
    return cue_metadata, run

# Function to extract run information from filenames
def extract_run(filename):
    match = re.search(r'_run-(\d+)_', filename)
    return match.group(1) if match else None

# Function to map social files to cue metadata
def map_social_to_cue(filename):
    run = extract_run(filename)
    if run in cue_metadata_dict:
        return cue_metadata_dict[run]
    return None

def is_equivalent(val1, val2, tolerance=1):
    return abs(val1 - val2) <= tolerance
# TODO:

def calc_adjusted_angle_df(df, x_col, y_col, xcenter, ycenter):
    # Vectorized calculation of angles
    angles = np.arctan2((ycenter - df[y_col]), (df[x_col] - xcenter))
    
    # Adjust the angle so it's between 0 and π radians
    angles = np.pi - angles
    
    # Convert angles to degrees and ensure they are positive
    angles_deg = np.abs(np.degrees(angles))
    
    # Ensure all angles fall within the 0 to 180 range
    angles_deg = angles_deg % 360
    angles_deg[angles_deg > 180] = 360 - angles_deg[angles_deg > 180]
    
    return angles_deg

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


def is_equivalent(val1, val2, tolerance=1):
    return abs(val1 - val2) <= tolerance

# %% ---------------------------------------------------------------------------
#  1. add task-social runtype metadata & 2. harmonize scans tsv and nifti files
# ------------------------------------------------------------------------------


scans_list = sorted(glob.glob('sub-*/**/*scans*.tsv', recursive=True))
for scan_fname in scans_list:
    # NOTE: Step 1: Get the scans.tsv using datalad
    run_command(f"datalad get {scan_fname}")
    # Check if scans_file is not empty and unlock it using git annex
    if os.path.exists(scan_fname) and os.path.getsize(scan_fname) > 0:
        run_command(f"git annex unlock {scan_fname}")

    scans_df = pd.read_csv(scan_fname, sep='\t')

    # NOTE: Step 2: Define the directory containing the task-cue event files
    cue_events_dir = './' + os.path.dirname( scan_fname) + '/func'
    cue_event_files = sorted([f for f in os.listdir(cue_events_dir) if 'task-cue' in f and f.endswith('_events.tsv')])

    # NOTE: Step 3: Function to extract cue metadata and run information from filenames
    # Create a dictionary to map run to cue metadata
    cue_metadata_dict = {}
    for file in cue_event_files:
        metadata, run = extract_cue_metadata_and_run(file)
        cue_metadata_dict[run] = metadata


    # NOTE: Step 4: Apply the function to add the task-social_runtype column
    scans_df['task-social_runtype'] = scans_df['filename'].apply(lambda x: map_social_to_cue(x) if 'task-social' in x else None)
    scans_df['task-social_runtype'].fillna('n/a', inplace=True)


    # NOTE: Step 5: if events file and niftifiles disagree, delete files
    nifti_files, event_files = list_nifti_and_event_files(cue_events_dir)
    orphan_files = remove_orphan_nifti_files(nifti_files, event_files)
    if orphan_files:
        for orphan_file in orphan_files:
            print(f"Removing {orphan_file}")
            run_command(f"git rm {orphan_file}")
            scans_df = scans_df[scans_df['filename'] != os.path.basename(orphan_file)]

    # Save the updated DataFrame back to the scans_file
    scans_df.to_csv(scan_fname, index=False)

    # Add the updated scans_file back to git annex
    run_command(f"git annex add {scan_fname}")
    run_command(f"git commit -m 'DOC: update scans tsv with task-social runtype metadata and remove orphan NIfTI files'")

    
    # run_command(f"git annex add {scan_fname}")
    # run_command(f"git commit -m 'DOC: update scans tsv and remove orphan NIfTI files'")
    # NOTE: Step 6: ultimately, delete BIDS data
    for event_fname in cue_event_files:
        event_fpath = os.path.join(cue_events_dir, event_fname)
        run_command(f"git rm {event_fpath}")
    run_command(f"git commit -m 'DEP: delete non-bids compliant events file'")




# %% ---------------------------------------------------------------------------
#                                   Parameters
# ------------------------------------------------------------------------------

bids_dir = '/Users/h/Documents/projects_local/1076_spacetop' # the top directory of datalad
code_dir = '/Users/h/Documents/projects_local/1076_spacetop/code' # where this code live
source_dir = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata'# where the source behavioral directory lives
beh_inputdir = join(source_dir, 'd_beh')

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


# %% ---------------------------------------------------------------------------
#                           3. Cognitive BIDSify
# ------------------------------------------------------------------------------


task_name = 'cognitive'
cognitive_flist = glob.glob(join(beh_inputdir,'sub-*', '**','task-social', '**', f'*{task_name}*.csv'), recursive=True)
filtered_cognitive_flist = [file for file in cognitive_flist if "sub-0001" not in file]


# Step 2: Configure the logging system
logging.basicConfig(filename='task-cue_vicarious.log',  # Log file path
                    filemode='w',            # Append mode ('w' for overwrite)
                    level=logging.INFO,     # Logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log message format

# Step 3: Create a logger object
logger = logging.getLogger('cognitive')

for cognitive_fpath in sorted(filtered_cognitive_flist):

    # 1. create an empty dataframe to host new BIDS data _______________________
    bids_beh = pd.DataFrame(columns=[
        'onset', 'duration', 'run_type', 'trial_type','trial_index','cue', 'stimulusintensity', 
        'rating_value', 'rating_glmslabel', 'rating_value_fillna', 
        'rating_glmslabel_fillna','rating_mouseonset','rating_mousedur',
        'stim_file', 
        'pain_onset_ttl1', 'pain_onset_ttl2', 'pain_onset_ttl3', 'pain_onset_ttl4', 'pain_stimulus_delivery_success',
        'cognitive_correct_response', 'cognitive_participant_response', 'cognitive_response_accuracy'])

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
    
    try:
        if trajectory_glob:
            trajectory_fname = trajectory_glob[0]
            traj_df = pd.read_csv(trajectory_fname)
        else:
            # If trajectory_glob is empty, raise a custom exception
            raise FileNotFoundError("Trajectory preproc DOES NOT exist")
            
    except FileNotFoundError as e:
        logger.warning(str(e))
        continue 
    except Exception as e:
        # This catches any other exceptions that might occur
        logger.error("An error occurred while processing the trajectory file: %s", str(e))
        continue


    # 3-1. calculate degree based on x, y coordinate


    # 3-2. Calculate the angle in radians and then convert to degrees 
    traj_df['expectangle_degrees'] = calc_adjusted_angle_df(
        traj_df, 'expectrating_end_x', 'expectrating_end_y', trajectory_x, trajectory_y)
    traj_df['outcomeangle_degrees'] = calc_adjusted_angle_df(
        traj_df, 'outcomerating_end_x', 'outcomerating_end_y', trajectory_x, trajectory_y)



    # 3-3. check if the calculated new degree matches the one in beh_df
    beh_df['event02_expect_fillna'] = beh_df['event02_expect_angle'].round(2)
    beh_df['event02_expect_fillna'].fillna(traj_df['adjusted_expectangle_degrees'].round(2), inplace=True)
    comparison_series = (beh_df['event02_expect_fillna'].round(2) == traj_df['adjusted_expectangle_degrees'].round(2))
    traj_df['comparison_flag'] = ~comparison_series
    expect_overall_flag = traj_df['comparison_flag'].any()
    if expect_overall_flag:
        discrepancy_indices = traj_df[traj_df['comparison_flag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tExpect Rating {idx}: (traj_df): {traj_df.loc[idx]['adjusted_expectangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event02_expect_fillna']}")

    beh_df['event04_outcome_fillna'] = beh_df['event04_actual_angle'].round(2)
    beh_df['event04_outcome_fillna'].fillna(traj_df['adjusted_outcomeangle_degrees'].round(2), inplace=True)
    outcome_comparison_mask = (beh_df['event04_actual_angle'].round(2) == traj_df['adjusted_outcomeangle_degrees'].round(2))
    traj_df['outcome_comparisonflag'] = ~outcome_comparison_mask
    outcome_overall_flag = traj_df['outcome_comparisonflag'].any()

    if outcome_overall_flag:
        discrepancy_indices = traj_df[traj_df['outcome_comparisonflag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tOutcome Rating {idx} (traj_df): {traj_df.loc[idx]['adjusted_outcomeangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event04_outcome_fillna']}")

    
    # map it to new label
    # 4. cue ___________________________________________________________________
    cue['onset'] = (beh_df['event01_cue_onset'] - trigger).round(2)
    cue['duration'] = (beh_df['ISI01_onset'] - beh_df['event01_cue_onset']).round(2)
    cue['run_type'] = task_name
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
    # cue['stim_file'] = beh_df["event01_cue_filename"]
    cue['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'/task-social/cue/runtype-{task_name}/{"sch" if x.startswith("h") else "scl"}' + x
    )
    cue['pain_onset_ttl1'] = "n/a"
    cue['pain_onset_ttl2'] = "n/a"
    cue['pain_onset_ttl3'] = "n/a"
    cue['pain_onset_ttl4'] = "n/a"
    cue['pain_stimulus_delivery_success'] = "n/a"
    cue['cognitive_correct_response'] = "n/a"
    cue['cognitive_participant_response'] = "n/a"
    cue['cognitive_response_accuracy'] = "n/a"

          
    # 5. expect ________________________________________________________________
    expect['onset'] = (beh_df['event02_expect_displayonset'] - trigger).round(2)
    expect['duration'] = (beh_df['event02_expect_RT']).round(2)
    expect['run_type'] = task_name
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
    expect['stimulusintensity'] = "n/a"
    expect['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'/task-social/cue/runtype-{task_name}/{"sch" if x.startswith("h") else "scl"}' + x
    )
    expect['pain_onset_ttl1'] = "n/a"
    expect['pain_onset_ttl2'] = "n/a"
    expect['pain_onset_ttl3'] = "n/a"
    expect['pain_onset_ttl4'] = "n/a"
    expect['pain_stimulus_delivery_success'] = "n/a"
    expect['cognitive_correct_response'] = "n/a"
    expect['cognitive_participant_response'] = "n/a"
    expect['cognitive_response_accuracy'] = "n/a"
    
    # 6. stim __________________________________________________________________

    stim['onset'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
    stim['duration'] = (beh_df['ISI03_onset'] - beh_df['event03_stimulus_displayonset']).round(2)
    stim['run_type'] = task_name
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
    stim['stim_file'] = '/task-social/cue/runtype-{task_name}/' + beh_df['event03_C_stim_filename'] 

    stim['pain_onset_ttl1'] = "n/a"
    stim['pain_onset_ttl2'] = "n/a"
    stim['pain_onset_ttl3'] = "n/a"
    stim['pain_onset_ttl4'] = "n/a"
    stim['pain_stimulus_delivery_success'] = "n/a"    
    stim['cognitive_correct_response'] = beh_df['event03_C_stim_match']
    stim['cognitive_participant_response'] = beh_df['event03_stimulusC_responsekeyname'].map({'right':'same', 'left':'diff'})
    stim['cognitive_response_accuracy'] = stim['cognitive_correct_response'] == stim['cognitive_participant_response']


    # outcome __________________________________________________________________
    outcome['onset'] = (beh_df['event04_actual_displayonset'] - trigger).round(2)
    outcome['duration'] = beh_df['event04_actual_RT'].round(2)
    outcome['run_type'] = task_name
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
    outcome['stim_file'] = 'task-social/outcomerating/task-cognitive_scale.png'
    outcome['pain_onset_ttl1'] = "n/a"
    outcome['pain_onset_ttl2'] = "n/a"
    outcome['pain_onset_ttl3'] = "n/a"
    outcome['pain_onset_ttl4'] = "n/a"
    outcome['pain_stimulus_delivery_success'] = "n/a"  
    outcome['cognitive_correct_response'] = "n/a"
    outcome['cognitive_participant_response'] = "n/a"
    outcome['cognitive_response_accuracy'] = "n/a"


    events = pd.concat([cue, expect, stim, outcome], ignore_index=True)
    events_sorted = events.sort_values(by='onset')
    events_sorted.fillna('n/a', inplace=True)
    if os.path.exists(beh_savedir) and os.path.isdir(beh_savedir):
        events_sorted.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-social_{run_bids}_events.tsv"), sep='\t', index=False)
    else:
        logger.critical(f"WARNING: The directory {beh_savedir} does not exist.")
    
    # extract bids info and save as new file



# %% ---------------------------------------------------------------------------
#                           3. Pain BIDSify
# ------------------------------------------------------------------------------
task_name = 'pain'
pain_flist = glob.glob(join(beh_inputdir,'sub-*', '**','task-social', '**', f'*{task_name}*.csv'), recursive=True)
filtered_pain_flist = [file for file in pain_flist if "sub-0001" not in file]

# %%
# Create a custom logger _______________________________________________________
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
info_handler = logging.FileHandler('task-cue_pain_info.log', mode='w')
info_handler.setLevel(logging.INFO)

warning_handler = logging.FileHandler('task-cue_pain_warning.log',  mode='w')
warning_handler.setLevel(logging.WARNING)

# Create formatters and add them to the handlers
info_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
warning_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
info_handler.setFormatter(info_format)
warning_handler.setFormatter(warning_format)
logger.addHandler(info_handler)
logger.addHandler(warning_handler)

for pain_fpath in sorted(filtered_pain_flist):

    # 1. create an empty dataframe to host new BIDS data _______________________
    bids_beh = pd.DataFrame(columns=[
        'onset', 'duration', 'run_type', 'trial_type','trial_index','cue', 'stimulusintensity', 
        'rating_value', 'rating_glmslabel', 'rating_value_fillna', 
        'rating_glmslabel_fillna','rating_mouseonset','rating_mousedur',
        'stim_file', 
        'pain_onset_ttl1', 'pain_onset_ttl2', 'pain_onset_ttl3', 'pain_onset_ttl4', 'pain_stimulus_delivery_success',
        'cognitive_correct_response', 'cognitive_participant_response', 'cognitive_response_accuracy'])
        
    cue = bids_beh.copy();
    expect = bids_beh.copy();
    stim = bids_beh.copy();
    outcome = bids_beh.copy();
    logger.info(f"\n\n{pain_fpath}")   


    # 2. extract metadata from original behavioral file ________________________
    pain_fname = os.path.basename(pain_fpath)
    sub_bids = re.search(r'sub-\d+', pain_fname).group(0)
    ses_bids = re.search(r'ses-\d+', pain_fname).group(0)
    run_bids = re.search(r'run-\d+', pain_fname).group(0)
    runtype = re.search(r'run-\d+-(\w+?)_', pain_fname).group(1)

    logger.info(f"_______ {sub_bids} {ses_bids} {run_bids} {runtype} _______")
    beh_savedir = join(bids_dir, sub_bids, ses_bids, 'func')
    beh_df = pd.read_csv(pain_fpath)
    trigger = beh_df['param_trigger_onset'][0]

    # 3. load trajectory data and calculate ratings ____________________________
    trajectory_glob = glob.glob(join(beh_inputdir, sub_bids, 'task-cue', ses_bids, 
                                     f"{sub_bids}_{ses_bids}_task-cue_{run_bids}_runtype-{runtype}_beh-preproc.csv"))
    try:
        if trajectory_glob:
            trajectory_fname = trajectory_glob[0]
            traj_df = pd.read_csv(trajectory_fname)
        else:
            # If trajectory_glob is empty, raise a custom exception
            raise FileNotFoundError("Trajectory preproc DOES NOT EXIST")
            
    except FileNotFoundError as e:
        logger.warning(str(e))
        logger.warning("Trajectory preproc DOES NOT EXIST")
        continue 
    except Exception as e:
        # This catches any other exceptions that might occur
        logger.error("An error occurred while processing the trajectory file: %s", str(e))
        continue


    # 3-1. calculate degree based on x, y coordinate
    # 3-2. Calculate the angle in radians and then convert to degrees 
    traj_df['expectangle_degrees'] = calc_adjusted_angle_df(
        traj_df, 'expectrating_end_x', 'expectrating_end_y', trajectory_x, trajectory_y)
    traj_df['outcomeangle_degrees'] = calc_adjusted_angle_df(
        traj_df, 'outcomerating_end_x', 'outcomerating_end_y', trajectory_x, trajectory_y)


    # 3-3. check if the calculated new degree matches the one in beh_df
    beh_df['event02_expect_fillna'] = beh_df['event02_expect_angle'].round(2)
    beh_df['event02_expect_fillna'].fillna(traj_df['adjusted_expectangle_degrees'].round(2), inplace=True)
    comparison_series = (beh_df['event02_expect_fillna'].round(2) == traj_df['adjusted_expectangle_degrees'].round(2))
    traj_df['comparison_flag'] = ~comparison_series
    expect_overall_flag = traj_df['comparison_flag'].any()
    if expect_overall_flag:
        discrepancy_indices = traj_df[traj_df['comparison_flag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tExpect Rating {idx}: (traj_df): {traj_df.loc[idx]['adjusted_expectangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event02_expect_fillna']}")

    beh_df['event04_outcome_fillna'] = beh_df['event04_actual_angle'].round(2)
    beh_df['event04_outcome_fillna'].fillna(traj_df['adjusted_outcomeangle_degrees'].round(2), inplace=True)
    outcome_comparison_mask = (beh_df['event04_actual_angle'].round(2) == traj_df['adjusted_outcomeangle_degrees'].round(2))
    traj_df['outcome_comparisonflag'] = ~outcome_comparison_mask
    outcome_overall_flag = traj_df['outcome_comparisonflag'].any()

    if outcome_overall_flag:
        discrepancy_indices = traj_df[traj_df['outcome_comparisonflag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tOutcome Rating {idx} (traj_df): {traj_df.loc[idx]['adjusted_outcomeangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event04_outcome_fillna']}")

    

    # 4. cue ___________________________________________________________________
    cue['onset'] = (beh_df['event01_cue_onset'] - trigger).round(2)
    cue['duration'] = (beh_df['ISI01_onset'] - beh_df['event01_cue_onset']).round(2)
    cue['run_type'] = task_name
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
    cue['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'/task-social/cue/runtype-{task_name}/{"sch" if x.startswith("h") else "scl"}' + x
    )
    cue['pain_onset_ttl1'] = "n/a"
    cue['pain_onset_ttl2'] = "n/a"
    cue['pain_onset_ttl3'] = "n/a"
    cue['pain_onset_ttl4'] = "n/a"
    cue['pain_stimulus_delivery_success'] = "n/a"
    cue['cognitive_correct_response'] = "n/a"
    cue['cognitive_participant_response'] = "n/a"
    cue['cognitive_response_accuracy'] = "n/a"
          
    # 5. expect ________________________________________________________________
    expect['onset'] = (beh_df['event02_expect_displayonset'] - trigger).round(2)
    expect['duration'] = (beh_df['event02_expect_RT']).round(2)
    expect['run_type'] = task_name
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
    expect['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'/task-social/cue/runtype-{task_name}/{"sch" if x.startswith("h") else "scl"}' + x
    )
    # expect['stim_file'] = beh_df["event01_cue_filename"]
    expect['pain_onset_ttl1'] = "n/a"
    expect['pain_onset_ttl2'] = "n/a"
    expect['pain_onset_ttl3'] = "n/a"
    expect['pain_onset_ttl4'] = "n/a"
    expect['pain_stimulus_delivery_success'] = "n/a"
    expect['cognitive_correct_response'] = "n/a"
    expect['cognitive_participant_response'] = "n/a"
    expect['cognitive_response_accuracy'] = "n/a"
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
    stim['run_type'] = task_name
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
    stim['stim_file'] = beh_df['event03_stimulus_type'].map(temperature_map) 
    if ttl_glob:
        stim['pain_onset_ttl1'] = (ttl_df['TTL1']).round(2)
        stim['pain_onset_ttl2'] = (ttl_df['TTL2']).round(2)
        stim['pain_onset_ttl3'] = (ttl_df['TTL3']).round(2)
        stim['pain_onset_ttl4'] = (ttl_df['TTL4']).round(2)
    else:
        stim['pain_onset_ttl1'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
        stim['pain_onset_ttl2'] = (stim['onset_ttl1'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['rampup'])).round(2)
        stim['pain_onset_ttl3'] = (stim['onset_ttl2'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['plateau'])).round(2)
        stim['pain_onset_ttl4'] = (stim['onset_ttl3'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['rampdown'])).round(2)
    stim['pain_stimulus_delivery_success'] = beh_df['event03_stimulus_P_trigger'].apply(lambda x: "success" if x == "Command Recieved: TRIGGER_AND_Response: RESULT_OK" else "fail")
    stim['cognitive_correct_response'] = "n/a"
    stim['cognitive_participant_response'] = "n/a"
    stim['cognitive_response_accuracy'] = "n/a"


    # outcome __________________________________________________________________
    outcome['onset'] = (beh_df['event04_actual_displayonset'] - trigger).round(2)
    outcome['duration'] = beh_df['event04_actual_RT'].round(2)
    outcome['run_type'] = task_name
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
    outcome['stim_file'] = 'task-social/outcomerating/task-pain_scale.png'
    outcome['pain_onset_ttl1'] = "n/a"
    outcome['pain_onset_ttl2'] = "n/a"
    outcome['pain_onset_ttl3'] = "n/a"
    outcome['pain_onset_ttl4'] = "n/a"
    outcome['pain_stimulus_delivery_success'] = beh_df['event03_stimulus_P_trigger'].apply(lambda x: "success" if x == "Command Recieved: TRIGGER_AND_Response: RESULT_OK" else "fail")
    outcome['cognitive_correct_response'] = "n/a"
    outcome['cognitive_participant_response'] = "n/a"
    outcome['cognitive_response_accuracy'] = "n/a"

    events = pd.concat([cue, expect, stim, outcome], ignore_index=True)
    events_sorted = events.sort_values(by='onset')
    events_sorted.fillna('n/a', inplace=True)
    if os.path.exists(beh_savedir) and os.path.isdir(beh_savedir):
        events_sorted.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-social_{run_bids}_events.tsv"), sep='\t', index=False)
    else:
        logger.critical(f"WARNING: The directory {beh_savedir} does not exist.")
    
    # extract bids info and save as new file

# %% ---------------------------------------------------------------------------
#                           3. Vicarious BIDSify
# ------------------------------------------------------------------------------
task_name = 'vicarious'
vicarious_flist = glob.glob(join(beh_inputdir,'sub-*', '**','task-social', '**', f'*{task_name}*.csv'), recursive=True)
filtered_vicarious_flist = [file for file in vicarious_flist if "sub-0001" not in file]
# 0. Configure the logging system
logging.basicConfig(filename='task-cue_vicarious.log',  # Log file path
                    filemode='w',            # Append mode ('w' for overwrite)
                    level=logging.INFO,     # Logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log message format

# Step 3: Create a logger object
logger = logging.getLogger('vicarious')
for vicarious_fpath in sorted(filtered_vicarious_flist):

    # 1. create an empty dataframe to host new BIDS data _______________________
    bids_beh = pd.DataFrame(columns=[
        'onset', 'duration', 'run_type', 'trial_type','trial_index','cue', 'stimulusintensity', 
        'rating_value', 'rating_glmslabel', 'rating_value_fillna', 
        'rating_glmslabel_fillna','rating_mouseonset','rating_mousedur',
        'stim_file', 
        'pain_onset_ttl1', 'pain_onset_ttl2', 'pain_onset_ttl3', 'pain_onset_ttl4', 'pain_stimulus_delivery_success',
        'cognitive_correct_response', 'cognitive_participant_response', 'cognitive_response_accuracy'])
    cue = bids_beh.copy();
    expect = bids_beh.copy();
    stim = bids_beh.copy();
    outcome = bids_beh.copy();
    logger.info(f"\n\n{vicarious_fpath}")   
    # 2. extract metadata from original behavioral file ________________________
    vicarious_fname = os.path.basename(vicarious_fpath)
    sub_bids = re.search(r'sub-\d+', vicarious_fname).group(0)
    ses_bids = re.search(r'ses-\d+', vicarious_fname).group(0)
    run_bids = re.search(r'run-\d+', vicarious_fname).group(0)
    runtype = re.search(r'run-\d+-(\w+?)_', vicarious_fname).group(1)


    logger.info(f"_______ {sub_bids} {ses_bids} {run_bids} {runtype} _______")
    beh_savedir = join(bids_dir, sub_bids, ses_bids, 'func')
    beh_df = pd.read_csv(vicarious_fpath)
    trigger = beh_df['param_trigger_onset'][0]

    # 3. load trajectory data and calculate ratings ____________________________
    trajectory_glob = glob.glob(join(beh_inputdir, sub_bids, 'task-cue', ses_bids, f"{sub_bids}_{ses_bids}_task-cue_{run_bids}_runtype-{runtype}_beh-preproc.csv"))
    
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
    traj_df['expectangle_degrees'] = calc_adjusted_angle_df(
        traj_df, 'expectrating_end_x', 'expectrating_end_y', trajectory_x, trajectory_y)
    traj_df['outcomeangle_degrees'] = calc_adjusted_angle_df(
        traj_df, 'outcomerating_end_x', 'outcomerating_end_y', trajectory_x, trajectory_y)


    # 3-3. check if the calculated new degree matches the one in beh_df
    beh_df['event02_expect_fillna'] = beh_df['event02_expect_angle'].round(2)
    beh_df['event02_expect_fillna'].fillna(traj_df['adjusted_expectangle_degrees'].round(2), inplace=True)
    comparison_series = ((beh_df['event02_expect_angle'].round(2)) == (traj_df['adjusted_expectangle_degrees'].round(2)))
    traj_df['comparison_flag'] = ~comparison_series
    expect_overall_flag = traj_df['comparison_flag'].any()
    if expect_overall_flag:
        discrepancy_indices = traj_df[traj_df['comparison_flag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tExpect Rating {idx}: (traj_df): {traj_df.loc[idx]['adjusted_expectangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event02_expect_fillna']}")

    beh_df['event04_outcome_fillna'] = beh_df['event04_actual_angle'].round(2)
    beh_df['event04_outcome_fillna'].fillna(traj_df['adjusted_outcomeangle_degrees'].round(2), inplace=True)
    outcome_comparison_mask = ((beh_df['event04_actual_angle'].round(2)) == (traj_df['adjusted_outcomeangle_degrees'].round(2)))
    traj_df['outcome_comparisonflag'] = ~outcome_comparison_mask
    outcome_overall_flag = traj_df['outcome_comparisonflag'].any()

    if outcome_overall_flag:
        discrepancy_indices = traj_df[traj_df['outcome_comparisonflag']].index
        for idx in discrepancy_indices:
            logger.info(f"\tOutcome Rating {idx} (traj_df): {traj_df.loc[idx]['adjusted_outcomeangle_degrees'].round(2)} \t(beh_df): {beh_df.loc[idx]['event04_outcome_fillna']}")


    # grab the intersection raise warning if dont match
    
    # map it to new label
    # 4. cue ___________________________________________________________________
    cue['onset'] = (beh_df['event01_cue_onset'] - trigger).round(2)
    cue['duration'] = (beh_df['ISI01_onset'] - beh_df['event01_cue_onset']).round(2)
    cue['run_type'] = task_name
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
    cue['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'/task-social/cue/runtype-{task_name}/{"sch" if x.startswith("h") else "scl"}' + x
    )
    cue['pain_onset_ttl1'] = "n/a"
    cue['pain_onset_ttl2'] = "n/a"
    cue['pain_onset_ttl3'] = "n/a"
    cue['pain_onset_ttl4'] = "n/a"
    cue['pain_stimulus_delivery_success'] = "n/a"
    cue['cognitive_correct_response'] = "n/a"
    cue['cognitive_participant_response'] = "n/a"
    cue['cognitive_response_accuracy'] = "n/a"
          
    # 5. expect ________________________________________________________________
    expect['onset'] = (beh_df['event02_expect_displayonset'] - trigger).round(2)
    expect['duration'] = (beh_df['event02_expect_RT']).round(2)
    expect['run_type'] = task_name
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
    expect['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'/task-social/cue/runtype-{task_name}/{"sch" if x.startswith("h") else "scl"}' + x
    )
    expect['pain_onset_ttl1'] = "n/a"
    expect['pain_onset_ttl2'] = "n/a"
    expect['pain_onset_ttl3'] = "n/a"
    expect['pain_onset_ttl4'] = "n/a"
    expect['pain_stimulus_delivery_success'] = "n/a"
    expect['cognitive_correct_response'] = "n/a"
    expect['cognitive_participant_response'] = "n/a"
    expect['cognitive_response_accuracy'] = "n/a"    
    # 6. stim __________________________________________________________________

    stim['onset'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
    stim['duration'] = (beh_df['ISI03_onset'] - beh_df['event03_stimulus_displayonset']).round(2)
    stim['run_type'] = task_name
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
    stim['stim_file'] = '/task-social/cue/runtype-{task_name}/' + beh_df['event03_stimulus_V_filename'] 
    stim['pain_onset_ttl1'] = "n/a"
    stim['pain_onset_ttl2'] = "n/a"
    stim['pain_onset_ttl3'] = "n/a"
    stim['pain_onset_ttl4'] = "n/a"
    stim['pain_stimulus_delivery_success'] = "n/a"  
    stim['cognitive_correct_response'] = "n/a"
    stim['cognitive_participant_response'] = "n/a"
    stim['cognitive_response_accuracy'] = "n/a"

    # outcome __________________________________________________________________
    outcome['onset'] = (beh_df['event04_actual_displayonset'] - trigger).round(2)
    outcome['duration'] = beh_df['event04_actual_RT'].round(2)
    outcome['run_type'] = task_name
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
    outcome['stim_file'] = 'task-social/outcomerating/task-vicarious_scale.png'
    outcome['pain_onset_ttl1'] = "n/a"
    outcome['pain_onset_ttl2'] = "n/a"
    outcome['pain_onset_ttl3'] = "n/a"
    outcome['pain_onset_ttl4'] = "n/a"
    outcome['pain_stimulus_delivery_success'] = "n/a"  
    outcome['cognitive_correct_response'] = "n/a"
    outcome['cognitive_participant_response'] = "n/a"
    outcome['cognitive_response_accuracy'] = "n/a"

    events = pd.concat([cue, expect, stim, outcome], ignore_index=True)
    events_sorted = events.sort_values(by='onset')
    events_sorted.fillna('n/a', inplace=True)
    if os.path.exists(beh_savedir) and os.path.isdir(beh_savedir):
        events_sorted.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-social_{run_bids}_events.tsv"), sep='\t', index=False)
    else:
        logger.critical(f"WARNING: The directory {beh_savedir} does not exist.")
    
    # extract bids info and save as new file