#!/usr/bin/env python

import numpy as np
import pandas as pd
import os, glob, re, json
from os.path import join
from pathlib import Path
import logging
import subprocess
import argparse

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"


# Configure the logger globally
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

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
        elif 'task-social' in file and file.endswith('_events.tsv'):
            event_files.append(file)

    return sorted(nifti_files), sorted(event_files)

def extract_bids(filename: str, key: str) -> str:
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    return bids_info_rmext[0]

def extract_run_and_task(filename):
    match = re.search(r'task-([a-zA-Z0-9]+)_.*_run-([0-9]+)', filename)
    if match:
        return match.groups()
    return None, None

def extract_cue_metadata_and_run(filename):
    cue_metadata = re.search(r'_desc-(\w+)_events\.tsv', filename).group(1)
    run = re.search(r'_run-(\d+)_', filename).group(1)
    return cue_metadata, run

def remove_orphan_nifti_files(nifti_files, event_files):
    event_file_basenames = [os.path.basename(f) for f in event_files]
    orphan_files = []

    for nifti_file in nifti_files:
        nifti_basename = os.path.basename(nifti_file)
        task, run = extract_run_and_task(nifti_basename)
        if task and run:
            expected_event_filename = f'sub-*_ses-*_task-social*_run-{run}_desc*_events.tsv'
            if not any(re.match(expected_event_filename.replace('*', '.*'), event_filename) for event_filename in event_file_basenames):
                orphan_files.append(nifti_file)
    return orphan_files

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

def categorize_rating(value):
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
    if value == "n/a" or pd.isna(value):
        return np.nan
    else:
        return pd.cut([value], bins=bins, labels=labels, right=True)[0]

def is_equivalent(val1, val2, tolerance=1):
    return abs(val1 - val2) <= tolerance

def extract_bids(filename: str, key: str) -> str:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extension, code will remove it.
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    return bids_info_rmext[0]

def get_task_type(bids_string, metadata_df):
    fname = Path(str(bids_string)).name
    sub = extract_bids(fname, 'sub')
    ses = extract_bids(fname, 'ses')
    run_column = extract_bids(fname, 'run')
    filtered_df = metadata_df[(metadata_df['sub'] == sub) & (metadata_df['ses'] == ses)]
    if not filtered_df.empty:
        return filtered_df[run_column].values[0]
    else:
        return None

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

def parse_args():
    parser = argparse.ArgumentParser(description="Process behavioral files for specific subjects or all subjects.")
    parser.add_argument('--bids_string', type=str, help="BIDS formatted string in format: sub-{sub%4d} ses-{ses%2d} task-{task} run-{run%2d}")
    parser.add_argument('--bids_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop', help="curated top directory of datalad.")
    parser.add_argument('--code_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop/code', help="where this code lives.")
    parser.add_argument('--source_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop/sourcedata', help="where this code lives.")
    return parser.parse_args()

args = parse_args()
bids_string = args.bids_string
bids_dir = args.bids_dir
code_dir = args.code_dir
source_dir = args.source_dir
beh_inputdir = join(source_dir, 'd_beh')

def process_task(task_name, filtered_file_list, logger, metadata_df):

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

    for file_path in sorted(filtered_file_list):
        # Create an empty dataframe to host new BIDS data
        bids_beh = pd.DataFrame(columns=[
            'onset', 'duration', 'run_type', 'trial_type', 'trial_index', 'cue', 'stimulusintensity',
            'rating_value', 'rating_glmslabel', 'rating_value_fillna',
            'rating_glmslabel_fillna', 'rating_mouseonset', 'rating_mousedur',
            'stim_file', 'pain_onset_ttl1', 'pain_onset_ttl2', 'pain_onset_ttl3',
            'pain_onset_ttl4', 'pain_stimulus_delivery_success',
            'cognitive_correct_response', 'cognitive_participant_response', 'cognitive_response_accuracy'
        ])

        cue = bids_beh.copy()
        expect = bids_beh.copy()
        stim = bids_beh.copy()
        outcome = bids_beh.copy()

        logger.info(f"\n\n{file_path}")

        # Extract metadata from original behavioral file
        file_name = os.path.basename(file_path)
        sub_bids = re.search(r'sub-\d+', file_name).group(0)
        ses_bids = re.search(r'ses-\d+', file_name).group(0)
        run_bids = re.search(r'run-\d+', file_name).group(0)
        bids_subsesrun = f"{sub_bids}_{ses_bids}_{run_bids}"
        runtype = get_task_type(bids_subsesrun, metadata_df)

        logger.info(f"_______ {sub_bids} {ses_bids} {run_bids} {runtype} _______")
        beh_savedir = join(bids_dir, sub_bids, ses_bids, 'func')
        beh_df = pd.read_csv(file_path)
        trigger = beh_df['param_trigger_onset'][0]

        # Load trajectory data and calculate ratings
        trajectory_glob = glob.glob(join(beh_inputdir, sub_bids, 'task-social', ses_bids,
                                         f"{sub_bids}_{ses_bids}_task-social_{run_bids}_runtype-{runtype}_beh-preproc.csv"))
        traj_df = None

        if trajectory_glob:
            try:
                trajectory_fname = trajectory_glob[0]
                traj_df = pd.read_csv(trajectory_fname)
                # Step 2: Calculate degrees based on x, y coordinates
                traj_df['adjusted_expectangle_degrees'] = calc_adjusted_angle_df(
                    traj_df, 'expectrating_end_x', 'expectrating_end_y', trajectory_x, trajectory_y)
                traj_df['adjusted_outcomeangle_degrees'] = calc_adjusted_angle_df(
                    traj_df, 'outcomerating_end_x', 'outcomerating_end_y', trajectory_x, trajectory_y)

                # Step 3: Check if the calculated new degree matches the one in beh_df
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

            except Exception as e:
                logger.error(f"An error occurred while processing the trajectory file: {e}")
        else:
            if args.bids_string:
                beh_df['event02_expect_fillna'] = 'n/a'
                beh_df['event04_outcome_fillna'] = 'n/a'
                logger.info(f"Skipping trajectory processing for {args.bids_string} as no trajectory file exists.")
            else:
                logger.warning(f"No trajectory data found for {sub_bids}, {ses_bids}, {run_bids}. No BIDS string provided.")

        # Process cue, expect, stim, outcome, and save to CSV
        process_behavioral_data(cue, expect, stim, outcome, beh_df, traj_df, trigger, task_name, beh_savedir, sub_bids, ses_bids, run_bids, logger)


def process_behavioral_data(cue, expect, stim, outcome, beh_df, traj_df, trigger, task_name, beh_savedir, sub_bids, ses_bids, run_bids, logger):
    # Cue ______________________________________________________________________
    cue['onset'] = (beh_df['event01_cue_onset'] - trigger).round(2)
    cue['duration'] = (beh_df['ISI01_onset'] - beh_df['event01_cue_onset']).round(2)
    cue['run_type'] = task_name
    cue['trial_type'] = 'cue'
    cue['trial_index'] = beh_df.index + 1
    cue['cue'] = beh_df['event01_cue_type']
    cue['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'task-social/cue/runtype-{task_name}/{"sch/" if x.startswith("h") else "scl/"}' + x
    )
    # Expect ___________________________________________________________________
    expect['onset'] = (beh_df['event02_expect_displayonset'] - trigger).round(2)
    expect['duration'] = (beh_df['event02_expect_RT']).round(2)
    expect['run_type'] = task_name
    expect['trial_type'] = 'expectrating'
    expect['trial_index'] = beh_df.index + 1
    expect['rating_value'] = beh_df['event02_expect_angle'].round(2)
    expect['rating_value_fillna'] = beh_df['event02_expect_fillna'].round(2)
    expect['rating_glmslabel'] = expect['rating_value'].apply(categorize_rating)
    expect['rating_glmslabel_fillna'] = expect['rating_value_fillna'].apply(categorize_rating)

    if traj_df is not None:
        expect['rating_mouseonset'] = (traj_df['expect_motiononset']).round(2)
        expect['rating_mousedur'] = (traj_df['expect_motiondur']).round(2)
    else:
        expect['rating_mouseonset'] = 'n/a'
        expect['rating_mousedur'] = 'n/a'

    expect['cue'] = beh_df['event01_cue_type']
    expect['stim_file'] = beh_df["event01_cue_filename"].apply(
        lambda x: f'task-social/cue/runtype-{task_name}/{"sch/" if x.startswith("h") else "scl/"}' + x
    )
    # Stim _____________________________________________________________________
    if task_name == 'pain':
        ttldir = '/Volumes/spacetop_projects_cue/data/fmri/fmri01_onset/onset02_SPM'

        ttl_glob = glob.glob(join(ttldir, sub_bids, ses_bids, 
                                f"{sub_bids}_{ses_bids}_task-social_{run_bids}_runtype-{task_name}_events_ttl.tsv"), recursive=True)
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
        'high_stim': '50_celsius',
        'med_stim': '49_celsius',
        'low_stim': '48_celsius'
        }
        stim['onset'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
        if ttl_glob: 
            stim['duration'] = (ttl_df['TTL4'] - ttl_df['TTL1']).round(2)
        else:
            stim['duration'] = ((beh_df['event03_stimulus_displayonset']-trigger) + beh_df['total_stimulus_time']).round(2) - (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
    else:
        stim['onset'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
        stim['duration'] = 5
    stim['run_type'] = task_name
    stim['trial_type'] = 'stimulus'
    stim['trial_index'] = beh_df.index + 1
    stim['stimulusintensity'] = beh_df['event03_stimulus_type']
    stim['cue'] = beh_df['event01_cue_type'] # if same as param_cue_type
    stim['stimulusintensity'] =  beh_df['event03_stimulus_type']
    if task_name == 'vicarious':
        stim['stim_file'] = f'task-social/stim/runtype-{task_name}/' + beh_df['event03_stimulus_V_filename'] 
    elif task_name == 'cognitive':
        stim['stim_file'] = f'task-social/stim/runtype-{task_name}/' + beh_df['event03_C_stim_filename'] 
    elif task_name == 'pain': 
        stim['stim_file'] = 'n/a'

    if task_name == 'pain':
        if ttl_glob:
            stim['pain_onset_ttl1'] = (ttl_df['TTL1']).round(2)
            stim['pain_onset_ttl2'] = (ttl_df['TTL2']).round(2)
            stim['pain_onset_ttl3'] = (ttl_df['TTL3']).round(2)
            stim['pain_onset_ttl4'] = (ttl_df['TTL4']).round(2)
        else:
            stim['pain_onset_ttl1'] = (beh_df['event03_stimulus_displayonset'] - trigger).round(2)
            stim['pain_onset_ttl2'] = (stim['pain_onset_ttl1'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['rampup'])).round(2)
            stim['pain_onset_ttl3'] = (stim['pain_onset_ttl2'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['plateau'])).round(2)
            stim['pain_onset_ttl4'] = (stim['pain_onset_ttl3'] + beh_df['event03_stimulus_type'].apply(lambda x: stimulus_times[x]['rampdown'])).round(2)
        stim['pain_stimulus_delivery_success'] = beh_df['event03_stimulus_P_trigger'].apply(lambda x: "success" if x == "Command Recieved: TRIGGER_AND_Response: RESULT_OK" else "fail")

    if task_name == 'cognitive':
        stim['cognitive_correct_response'] = beh_df['event03_C_stim_match']
        stim['cognitive_participant_response'] = beh_df['event03_stimulusC_responsekeyname'].map({'right':'same', 'left':'diff'})
        stim['cognitive_response_accuracy'] = stim['cognitive_correct_response'] == stim['cognitive_participant_response']

    # Outcome __________________________________________________________________
    outcome['onset'] = (beh_df['event04_actual_displayonset'] - trigger).round(2)
    outcome['duration'] = beh_df['event04_actual_RT'].round(2)
    outcome['run_type'] = task_name
    outcome['trial_type'] = 'outcomerating'
    outcome['trial_index'] = beh_df.index + 1
    outcome['rating_value'] = beh_df['event04_actual_angle'].round(2)
    outcome['rating_value_fillna'] = beh_df['event04_outcome_fillna']
    outcome['rating_glmslabel'] = outcome['rating_value'].apply(categorize_rating)
    outcome['rating_glmslabel_fillna'] = outcome['rating_value_fillna'].apply(categorize_rating)

    if traj_df is not None:
        outcome['rating_mouseonset'] = (traj_df['expect_motiononset']).round(2)
        outcome['rating_mousedur'] = (traj_df['expect_motiondur']).round(2)
    else:
        outcome['rating_mouseonset'] = 'n/a'
        outcome['rating_mousedur'] = 'n/a'
    # outcome['rating_mouseonset'] = (traj_df['outcome_motiononset']).round(2)
    # outcome['rating_mousedur'] = (traj_df['outcome_motiondur']).round(2)

    outcome['cue'] = beh_df['event01_cue_type'] 
    outcome['stimulusintensity'] =  beh_df['event03_stimulus_type']
    outcome['stim_file'] = f'task-social/outcomerating/task-{task_name}_scale.png'
    if task_name == "pain":
        outcome['pain_stimulus_delivery_success'] = beh_df['event03_stimulus_P_trigger'].apply(lambda x: "success" if x == "Command Recieved: TRIGGER_AND_Response: RESULT_OK" else "fail")
    else:
        outcome['pain_stimulus_delivery_success'] = "n/a"  




    events = pd.concat([cue, expect, stim, outcome], ignore_index=True)
    events_sorted = events.sort_values(by='onset')
    if task_name == 'pain':
        events_sorted = events_sorted[events_sorted['pain_stimulus_delivery_success'].notna()]
    events_sorted.fillna('n/a', inplace=True)


    if os.path.exists(beh_savedir) and os.path.isdir(beh_savedir):
        events_sorted.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-social_acq-mb8_{run_bids}_events.tsv"), sep='\t', index=False)
    else:
        logger.critical(f"WARNING: The directory {beh_savedir} does not exist.")


def main():

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


    args = parse_args()
    bids_string = args.bids_string
    task_names = ['cognitive', 'pain', 'vicarious']
    logger_dict = {task: setup_logger(task, f'task-social_{task}.log') for task in task_names}
    code_dir = Path(__file__).resolve().parent
    print(code_dir)
    metadata_df = pd.read_csv(join(code_dir, 'spacetop_task-social_run-metadata_parameter.csv'))

    if args.bids_string is not None:
        task_name = get_task_type(args.bids_string, metadata_df)
        fname = Path(args.bids_string).name
        if task_name not in task_names:
            print(f"Task {task_name} is not recognized. Skipping...")
        else:
            sub = extract_bids(fname, 'sub')
            ses = extract_bids(fname, 'ses')
            run = extract_bids(fname, 'run')

            filtered_file_list = glob.glob(
                str(Path(beh_inputdir) / sub / '**' / 'task-social' / '**' / f'*{args.bids_string}*.csv'),
                recursive=True)

            if not filtered_file_list:
                temp_file_list = glob.glob(
                    str(Path(beh_inputdir) / sub / 'task-social' / ses / f'{sub}_{ses}_task-social_{run}*TEMP*.csv'))
                filtered_file_list = temp_file_list if temp_file_list else []

                if not filtered_file_list:
                    print(f'No behavior data file found for {sub}, {ses}, {run}.')
                    logger_dict[task_name].error(f"An error occurred while processing the trajectory file: {sub}, {ses}, {run}")
                    return

            process_task(task_name, filtered_file_list, logger_dict[task_name], metadata_df)
    else:
        for task_name in task_names:
            file_list = glob.glob(
                join(beh_inputdir, 'sub-*', '**', 'task-social', '**', f'*{task_name}*.csv'),
                recursive=True)
            filtered_file_list = [file for file in file_list if "sub-0001" not in file]
            process_task(task_name, filtered_file_list, logger_dict[task_name], metadata_df)


if __name__ == "__main__":
    main()


# %% HED tag
description_onset = {
    "LongName": "Onset time of event",
    "Description": "Marks the start of an ongoing event of temporal extent.",
    "Units": "s",
    "HED": "Property/Data-property/Data-marker/Temporal-marker/Onset"
}
description_duration = {
    "LongName": "The period of time during which an event occurs.",
    "Description": "Refers to duration of cue presentation or response time towards target item. (a) For valid_cue and invalid_cue, duration refers to the image presentation of cue. (b) For target_response, duration refers to response time to respond to target item. It is calculated as the interval between onset of button press and onset of target presentation ",
    "Units": "s",
    "HED": "Property/Data-property/Data-value/Spatiotemporal-value/Temporal-value/Duration"
    } 

description_runtype = {
    "LongName": "The type of subtasks within task-social",
    "Description": "Refers to the type of subtask: [pain, vicarious, cognitive']",
    "Levels": {
        "pain": "The stimuli being delivered is thermal heat.",
        "vicarious": "The stimuli being delivered is a video with patients in pain",
        "cognitive": "The stimuli being delivered is an image with two figures; participants are prompted to mentally rotate the figures and decide whether they are same or different"
        },
    "HED": {
        "pain": "Property/Sensory-property/Sensory-attribute/Somatic-attribute/Pain",
        "vicarious": "Action/Think/Judge",
        "cognitive": "Action/Think/Discriminate"
    }
} 

description_trialtype = {
    "LongName": "Type of epochs with each trial",
    "Description": "There are four epochs in each trial: cue, expectrating, stim, outcomerating",
    "Levels": {
        "cue": "Participants passively viewed a presentation of a high or low social cue, consisting of data points that participants believed indicated other people's ratings for that stimulus presented for 1 second on screen",
        "expectrating": "Participants provided ratings of their expectations on the upcoming stimulus intensity on a gLMS scale for a total duration of 4 seconds overlaid with the cue image",
        "stim": "Participants passively received/viewed experimentally delivered stimuli for each of the mental rotation, vicarious pain, and somatic pain tasks for 5 seconds each",
        "outcomerating": "Participants provided ratings on their subjective experience of cognitive effort, vicarious pain, or somatic pain for 4 seconds"
    },
    "HED": {
        "cue": "Property/Task-property/Task-stimulus-role/Cue",
        "expectrating": "Action/Think/Encode",
        "stim": "Action/Perceive",
        "outcomerating": "Action/Think/Encode"
    }
}

description_trialindex = {
    "LongName": "Trial order",
    "Description": "Indicates the trial order. There are a total of 12 trials in each run.",
    "HED": "Property/Data-property/Data-value/Quantitative-value/Item-index/1-12"
}

description_ratingvalue = {
    "LongName": "Rating value",
    "Description": "The rating degree on a semicircle scale",
    "HED": "Property/Data-property/Data-value/Quantitative-value/Item-interval/0-180"
}

description_ratingglms = {
    "LongName": "Labels of generalized Labeled Magnitude Scale (gLMS)",
    "Description": "Labels of generalized Labeled Magnitude Scale (gLMS)",
    "Levels": {
        "No sensation": "No sensation",
        "Barely detectable": "Barely detectable",
        "Weak": "Weak",
        "Moderate": "Moderate",
        "Strong": "Strong",
        "Very Strong": "Very Strong",
        "Strongest sensation of any kind": "Strongest sensation of any kind"
    },
    "HED": "Property/Data-property/Data-marker"
}
description_ratingvalueNA = {
    "LongName": "Rating value with imputed values from mouse trajectory data",
    "Description": "Using mouse trajectory data, we extract the last degree recorded on the scale. From this, we impute degrees for cells that were originally marked n/a",
    "HED": "Property/Data-property/Data-value/Quantitative-value/Item-interval/0-180"
}
description_ratingglmsNA = {
    "LongName": "Labels of generalized Labeled Magnitude Scale (gLMS)",
    "Description": "Labels of generalized Labeled Magnitude Scale (gLMS)",
    "Levels": {
        "No sensation": "No sensation",
        "Barely detectable": "Barely detectable",
        "Weak": "Weak",
        "Moderate": "Moderate",
        "Strong": "Strong",
        "Very Strong": "Very Strong",
        "Strongest sensation of any kind": "Strongest sensation of any kind"
    },
    "HED": "Property/Data-property/Data-marker"
}
description_ratingmouseonset = {
    "LongName": "Onset time of mouse trajectory",
    "Description": "the time when the participant started moving the trackball in relation to the rating epoch",
    "Units": "s",
    "HED": "Property/Data-property/Data-marker/Temporal-marker/Onset"
}

description_mousedur = {
    "LongName": "The period of time during which an event occurs.",
    "Description": "Refers to duration of cue presentation or response time towards target item. (a) For valid_cue and invalid_cue, duration refers to the image presentation of cue. (b) For target_response, duration refers to response time to respond to target item. It is calculated as the interval between onset of button press and onset of target presentation ",
    "Units": "s",
    "HED": "Property/Data-property/Data-value/Spatiotemporal-value/Temporal-value/Duration"

}
description_cue = {
    "LongName": "A cue to indicate level of upcoming stimulus intensity",
    "Description": "Participants passively viewed a presentation of a high or low social cue, consisting of data points that participants believed indicated other people's ratings for that stimulus presented for 1 second on screen",
    "Levels": {
        "high_cue": "Data points on the cue indicate that past participants perceived the upcoming stimulus as having high intensity",
        "low_cue": "Data points on the cue indicate that past participants perceived the upcoming stimulus as having low intensity"
    },
    "HED": {
        "high_cue": ["Property/Task-property/Task-stimulus-role/Cue", "Property/Data-property/Data-value/Categorical-value/Categorical-level-value/High"],
        "low_cue": ["Property/Task-property/Task-stimulus-role/Cue", "Property/Data-property/Data-value/Categorical-value/Categorical-level-value/Low"]
    }
}

description_stimulusintensity = {
    "LongName": "",
    "Description": "",
    "Levels": {
        "high_stim": "High intensity stimulus (pain, vicarious, cognitive task)",
        "med_stim": "Medium intensity stimulus (pain, vicarious, cognitive task)",
        "low_stim": "Low intensity stimulus (pain, vicarious, cognitive task)"
    },
    "HED":  {
        "high_stim": ["Property/Task-property/Task-event-role/Experimental-stimulus", "Property/Data-property/Data-value/Categorical-value/Categorical-level-value/High"],
        "med_stim": ["Property/Task-property/Task-event-role/Experimental-stimulus", "Property/Data-property/Data-value/Categorical-value/Categorical-level-value/Medium"], 
        "low_stim": ["Property/Task-property/Task-event-role/Experimental-stimulus", "Property/Data-property/Data-value/Categorical-value/Categorical-level-value/Low"]
    }
}

description_stimfile = {
    "LongName": "stimulus file path",
    "Description": "Represents the location of the stimulus file (such as an image, video, or audio file) presented at the given onset time.",
    "HED": "Property/Task-property/Task-event-role/Experimental-stimulus"
}
description_painonset1 = {
    "LongName": "Onset time of pain stimulus (ramp up)",
    "Description": "Marks the start of an pain stimulus trigger.",
    "Units": "s",
    "HED": "Property/Data-property/Data-marker/Temporal-marker/Onset"
}
description_painonset2 = {
    "LongName": "Onset time of pain stimulus (reach plateau)",
    "Description": "Marks the start of when pain stimulus reaches intended temperature and starts plateau.",
    "Units": "s",
    "HED": "Property/Data-property/Data-marker/Temporal-marker/Onset"
}
description_painonset3 = {
    "LongName": "Onset time of pain stimulus (ramp down)",
    "Description": "Marks the end of an pain plateau.",
    "Units": "s",
    "HED": "Property/Data-property/Data-marker/Temporal-marker/Onset"
}
description_painonset4 = {
    "LongName": "Onset time of pain stimulus (baseline)",
    "Description": "Marks the end of a pain stimulus trigger, returning to baseline.",
    "Units": "s",
    "HED": "Property/Data-property/Data-marker/Temporal-marker/Onset"
}
description_painsuccess = {
    "LongName": "Onset time of pain stimulus (baseline)",
    "Description": "Marks the end of a pain stimulus trigger, returning to baseline.",
    "Units": "s",
    "HED": "Property/Data-property/Data-value/Categorical-value/Categorical-class-value/True"
}
description_cognitiveresponse = {
    "LongName": "Correct response for the rotated image",
    "Description": "Correct answer for whether two figures are same or different",
    "Levels": {
        "same": "The two figures are the same",
        "diff": "The two figures are different"
    },
    "HED": { 
        "same": "Action/Think/Discriminate", 
        "diff": "Action/Think/Discriminate"
        }
}
description_cognitiveparticipant = {
    "LongName": "Participant response for the rotated image",
    "Description": "Participant respond to two options -- same or diff -- to the two figures on screen",
    "Levels": {
        "same": "The two figures are the same",
        "diff": "The two figures are different"
    },
    "HED": { 
        "same": "Action/Think/Discriminate", 
        "diff": "Action/Think/Discriminate"
        }
}
description_cognitiveaccuracy = {
    "LongName": "Mental rotation task accuracy",
    "Description": "Marks the end of a pain stimulus trigger, returning to baseline.",
    "Levels": {
        "True": "Correct response in regards to image (correctly identified as old or new)",
        "False": "Incorrect response in regards to image (incorrectly identified as old or new)"
    },
    "HED": { 
        "True": "Property/Task-property/Task-action-type/Correct-action", 
        "False": "Property/Task-property/Task-action-type/Incorrect-action"
        }
}

events_json = {"onset": description_onset,
                "duration": description_duration, 
                "run_type": description_runtype, 
                "trial_type": description_trialtype,
                "trial_index": description_trialindex,
                "cue": description_cue, 
                "stimulusintensity": description_stimulusintensity, 
                "rating_value":description_ratingvalue,
                "rating_glmslabel": description_ratingglms,
                "rating_value_fillna": description_ratingvalueNA, 
                "rating_glmslabel_fillna": description_ratingglmsNA, 
                "rating_mouseonset": description_ratingmouseonset, 
                "rating_mousedur": description_mousedur, 
                "stim_file": description_stimfile, 
                "pain_onset_ttl1": description_painonset1, 
                "pain_onset_ttl2": description_painonset2, 
                "pain_onset_ttl3": description_painonset3, 
                "pain_onset_ttl4": description_painonset4, 
                "pain_stimulus_delivery_success": description_painsuccess, 
                "cognitive_correct_response": description_cognitiveresponse, 
                "cognitive_participant_response": description_cognitiveparticipant, 
                "cognitive_response_accuracy": description_cognitiveaccuracy
                }  


json_fname = join(bids_dir, f"task-social_events.json")
with open(json_fname, 'w') as file:
    json.dump(events_json, file, indent=4)