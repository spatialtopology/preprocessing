# Generate events files for task-narratives

# This script reads raw behavior data files from d_beh for task-narratives, extracts time stamps and design information, and stores them in new *events.tsv files accompanying BOLD files.

# For more information, please see README.md and the associated paper (Jung et al., 2024)

import os, re, glob
import pandas as pd
import numpy as np
import traceback
import argparse
from pathlib import Path
import requests

def extract_bids(filename: str, key: str) -> str:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extension, code will remove it.
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    return bids_info_rmext[0]

def get_column_value(df, column_name, default_value=''):
    """
    Safely get the value from a DataFrame column, returns default_value if column does not exist.
    """
    return df[column_name] if column_name in df else default_value

def create_event_row(onset, duration, trial_type, modality, stim_file, situation=None, context=None, response_x=None, response_y=None):
    """
    Creates a DataFrame row for an event with specified attributes.
    """
    return pd.DataFrame({
        "onset": onset,
        "duration": duration,
        "trial_type": trial_type,
        "response_x": response_x,
        "response_y": response_y,
        "situation": situation,
        "context": context,
        "modality": modality,
        "stim_file": stim_file
    }, index=[0])

def download_counterbalance_file(data_dir):
    url = 'https://raw.githubusercontent.com/spatialtopology/task-narratives/master/design/task-narratives_counterbalance_ver-01.csv'
    counterbalance_filename = os.path.join(data_dir, 'task-narratives_counterbalance_ver-01.csv')

    response = requests.get(url)
    with open(counterbalance_filename, 'wb') as file:
        file.write(response.content)

    DesignTable = pd.read_csv(counterbalance_filename)
    return DesignTable


def find_behavior_file(beh_inputdir, sub, ses, run):
    beh_fname = Path(beh_inputdir) / sub / 'task-narratives' / f'{sub}_{ses}_task-narratives_{run}.csv'
    
    # Check if the file exists and has data
    if beh_fname.is_file():
        # Try to read the file and check if it contains data
        try:
            beh_df = pd.read_csv(beh_fname)
            if not beh_df.empty:
                return beh_fname
            else:
                print(f"File {beh_fname} is empty. Attempting to find an alternative.")
        except pd.errors.EmptyDataError:
            print(f"File {beh_fname} exists but is empty. Attempting to find an alternative.")
        except Exception as e:
            print(f"Error reading file {beh_fname}: {e}. Attempting to find an alternative.")
    else:
        print(f"File {beh_fname} does not exist. Attempting to find an alternative.")

    # Attempt to find a temporary or alternative file
    temp_fpath = Path(beh_inputdir) / sub / 'task-narratives' / f'{sub}_{ses}_task-narratives_{run}*TEMP*.csv'
    
    if temp_fpath.is_file():
        try:
            beh_df = pd.read_csv(temp_fpath)
            if not beh_df.empty:
                return temp_fpath
            else:
                print(f"Temporary file {temp_fpath} is empty.")
        except pd.errors.EmptyDataError:
            print(f"Temporary file {temp_fpath} exists but is empty.")
        except Exception as e:
            print(f"Error reading temporary file {temp_fpath}: {e}")
    else:
        print(f"No behavior data file found for {sub}, {ses}, {run}. Checked both standard and temporary filenames.")
    
    return None

def narrative_format2bids(sub, ses, run, taskname, beh_inputdir, bids_dir):
    """
    Converts behavioral data from a raw format to a BIDS-compliant events.tsv file for narrative-based tasks.

    This function processes raw behavioral data, extracting timestamps and event information, and formats them 
    into a BIDS-compatible events.tsv file. The function handles various types of events, including narrative 
    presentation, ratings, and mouse trajectories, and computes relevant onset and duration times, adjusting for 
    the start time of the run.

    Parameters:
    -----------
    sub : str
        The subject identifier (e.g., 'sub-0001').
    ses : str
        The session identifier (e.g., 'ses-02').
    run : str
        The run identifier (e.g., '01', '02', etc.).
    taskname : str
        The task name (e.g., 'task-narratives').
    beh_inputdir : str
        The directory path where the raw behavioral data files are located.
    bids_dir : str
        The root directory of the BIDS dataset where the formatted events.tsv files will be saved.

    Returns:
    --------
    None

    Notes:
    ------
    - If the specified behavioral data file does not exist, the function prints a message and exits.
    - The function creates an events.tsv file with the following columns: onset, duration, trial_type, 
      response_x, response_y, situation, context, modality, stim_file.
    - The modality (Audio or Text) is determined based on the run number ('01' or '02' corresponds to Audio, 
      others correspond to Text).
    - Each event type (narrative presentation, ratings, mouse trajectories) is processed separately and added 
      to the events.tsv file.
    - The resulting events.tsv file is saved with 3 decimal places for onset and duration.
    - Missing values (NaN) are replaced with "n/a" in the output file.
    - Errors encountered during file saving are logged in an error_log.txt file within the BIDS directory.

    Raises:
    -------
    OSError:
        If there is an error saving the resulting events.tsv file, it will be logged and an error message 
        will be printed.

    Example:
    --------
    narrative_format2bids('sub-0001', 'ses-02', '01', 'task-narratives', '/path/to/beh_data', '/path/to/bids_data')
    """
    # fpath = os.path.join(beh_inputdir, sub, taskname, f'{sub}_{ses}_{taskname}_run-{run}_beh-preproc.csv')
    # if not os.path.isfile(fpath):
    #     print(f'No behavior data file for {sub}_run-{run}')
    #     return
    
    # beh_fname = Path(beh_inputdir) / sub / taskname / f'{sub}_{ses}_{taskname}_{run}_beh-preproc.csv'

    # if not beh_fname.is_file():
    # # Attempt to find a temporary or alternative file
    #     temp_fpath = Path(beh_inputdir) / sub / 'task-narratives' / f'{sub}_{ses}_task-narratives_{run}*TEMP*.csv'
        
    #     if temp_fpath.is_file():
    #         beh_fname = temp_fpath
    #     else:
    #         print(f'No behavior data file found for {sub}, {ses}, {run}. Checked both standard and temporary filenames.')
    #         return None
    # Construct the expected file path
    DesignTable = download_counterbalance_file(beh_inputdir)
    narratives = [[7, 8], [5, 6], [3, 4], [1, 2]]  # narrative presented in each run
    
    # Initial file search with wildcards
    beh_fname_pattern = str(Path(beh_inputdir) / sub / 'task-narratives' / f'{sub}_{ses}_task-narratives_{run}*preproc.csv')
    matching_files = glob.glob(beh_fname_pattern)
    
    if matching_files:
        beh_fname = Path(matching_files[0])
    else:
        # Check for the non-preproc file
        beh_fname = Path(beh_inputdir) / sub / 'task-narratives' / f'{sub}_{ses}_task-narratives_{run}_beh.csv'
        
        if not beh_fname.is_file():
            # Attempt to find a temporary or alternative file
            temp_pattern = str(Path(beh_inputdir) / sub / 'task-narratives' / f'{sub}_{ses}_task-narratives_{run}*TEMP*.csv')
            temp_files = glob.glob(temp_pattern)
            
            if temp_files:
                beh_fname = Path(temp_files[0])
            else:
                print(f'No behavior data file found for {sub}, {ses}, {run}. Checked both standard and temporary filenames.')
                return None
    
    # If a file is found, proceed to load it
    print(f"Using behavior file: {beh_fname}")
    
    try:
        source_beh = pd.read_csv(beh_fname)
        if source_beh.empty:
            print(f"The file {beh_fname} is empty.")
            return None
    except Exception as e:
        print(f"Failed to read the file {beh_fname}: {e}")
        return None
    
    # beh_fname = find_behavior_file(beh_inputdir, sub, ses, run)
    # source_beh = pd.read_csv(beh_fname)
    new_beh = pd.DataFrame(columns=["onset", "duration", "trial_type", 
                            "response_x", "response_y",
                            "situation", "context", "modality", "stim_file"])    # new events to store
    # if run in ['01', '02']:
    #     modality = 'Audio'
    # else:
    #     modality = 'Text'
    modality = 'Audio' if run in ['01', '02'] else 'Text'
    t_run_start = source_beh.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

    trial_num = len(source_beh)
    situation = [None] * trial_num
    context = [None] * trial_num
    r = int(run.split('-')[1]) - 1   # Adjust the run number to be zero-based
    for t in range(trial_num):    # each trial

        # Situation and context     
        if t < 9:
            situation_chunk = DesignTable.Situation[DesignTable.Narrative == narratives[r][t % 2]]
            situation[t] = situation_chunk.iloc[t]
            context_chunk = DesignTable.Context[DesignTable.Narrative == narratives[r][t % 2]]
            context[t] = context_chunk.iloc[t]
        else:
            situation_chunk = DesignTable.Situation[DesignTable.Narrative == narratives[r][1 - (t % 2)]]
            situation[t] = situation_chunk.iloc[t - 9]
            context_chunk = DesignTable.Context[DesignTable.Narrative == narratives[r][1 - (t % 2)]]
            context[t] = context_chunk.iloc[t - 9]
        source_beh['situation'] = situation
        source_beh['context'] = context

    for t in range(trial_num):    # each trial
        # Event 1. narrative presentation
        onset = source_beh.loc[t, 'event02_administer_onset'] - t_run_start
        duration = source_beh.loc[t, 'event03_feel_displayonset'] - source_beh.loc[t, 'event02_administer_onset']
        trial_type = "narrative_presentation"
        situation = source_beh.loc[t, 'situation']
        context = source_beh.loc[t, 'context']
        stim_file = f'task-narratives/{source_beh.loc[t, "param_stimulus_filename"][:20] + (".mp3" if run in ["01", "02"] else ".txt")}'
        new_row = create_event_row(onset, duration, trial_type, modality, stim_file, situation, context)
        new_beh = pd.concat([new_beh, new_row], ignore_index=True)

        # Event 2. feeling rating
        onset = source_beh.loc[t, 'event03_feel_displayonset'] - t_run_start
        # duration = source_beh.loc[t, 'RT_feeling'] if pd.notna(source_beh.loc[t, 'RT_feeling']) else source_beh.loc[t, 'RT_feeling_adj']
        if 'RT_feeling' in source_beh.columns:
            duration = source_beh.loc[t, 'RT_feeling'] if pd.notna(source_beh.loc[t, 'RT_feeling']) else source_beh.loc[t, 'RT_feeling_adj']
        elif 'RT_feeling_adj' in source_beh.columns:
            duration = source_beh.loc[t, 'RT_feeling_adj']
        else:
            duration = 'n/a'  # Or some default value if neither column exists

        trial_type = 'rating_feeling'
        response_x = get_column_value(source_beh, 'feeling_end_x')
        response_y = get_column_value(source_beh, 'feeling_end_y')
        new_row = create_event_row(onset, duration, trial_type, modality, stim_file, situation, context, response_x, response_y)
        new_beh = pd.concat([new_beh, new_row], ignore_index=True)
        
        # Event 3. feeling mouse trajectory
        # onset += source_beh.loc[t, 'motion_onset_feeling']
        # duration = source_beh.loc[t, 'motion_dur_feeling']
        if 'motion_onset_feeling' in source_beh.columns:
            onset += source_beh.loc[t, 'motion_onset_feeling']
            duration = source_beh.loc[t, 'motion_dur_feeling']
        else:
            onset = 'n/a'
            duration = 'n/a'
        trial_type = 'feeling_mouse_trajectory'
        new_row = create_event_row(onset, duration, trial_type, modality, stim_file, situation, context, response_x, response_y)
        new_beh = pd.concat([new_beh, new_row], ignore_index=True)

        # Event 4. expectation rating
        onset = source_beh.loc[t, 'event04_expect_displayonset'] - t_run_start
        # duration = source_beh.loc[t, 'RT_expectation'] if pd.notna(source_beh.loc[t, 'RT_expectation']) else source_beh.loc[t, 'RT_expectation_adj']
        if 'RT_expectation' in source_beh.columns:
            duration = source_beh.loc[t, 'RT_expectation'] if pd.notna(source_beh.loc[t, 'RT_expectation']) else source_beh.loc[t, 'RT_expectation_adj']
        elif 'RT_expectation_adj' in source_beh.columns:
            duration = source_beh.loc[t, 'RT_expectation_adj']
        else:
            duration = 'n/a'  # Or some default value if neither column exists
        trial_type = 'rating_expectation'
        response_x = get_column_value(source_beh, 'expectation_end_x')
        response_y = get_column_value(source_beh, 'expectation_end_y')
        new_row = create_event_row(onset, duration, trial_type, modality, stim_file, situation, context, response_x, response_y)
        new_beh = pd.concat([new_beh, new_row], ignore_index=True)

        # Event 5. expectation mouse trajectory
        if 'motion_onset_expectation' in source_beh.columns:
            onset += source_beh.loc[t, 'motion_onset_expectation']
            duration = source_beh.loc[t, 'motion_dur_expectation']
        else:
            onset = 'n/a'
            duration = 'n/a'
        trial_type = 'expectation_mouse_trajectory'
        new_row = create_event_row(onset, duration, trial_type, modality, stim_file, situation, context, response_x, response_y)
        new_beh = pd.concat([new_beh, new_row], ignore_index=True)

    # Change precisions and replace missing values
    new_beh = new_beh.round({'onset': 3, 'duration': 3}).replace(np.nan, 'n/a')
    new_fname = Path(bids_dir) / sub / 'ses-02' / 'func' / f'{sub}_ses-02_task-narratives_acq-mb8_{run}_events.tsv'

    try:
        new_beh.to_csv(new_fname, sep='\t', index=False)
    except OSError as e:
        with open(Path(bids_dir) / "error_log.txt", "a") as log_file:
            log_file.write(f"Error encountered for {sub}, {ses}, {run}: {e}\n")
            traceback.print_exc(file=log_file)
        print(f"An error occurred and has been logged: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Process behavioral files for specific subjects or all subjects.")
    parser.add_argument('--bids_string', type=str, help="BIDS formatted string in format: sub-{sub%04d}_ses-{ses%02d}_task-{task}_run-{run%02d}")
    parser.add_argument('--beh_inputdir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop/sourcedata/d_beh', help="Input directory where raw behavioral data lives.")
    parser.add_argument('--bids_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop', help="Base directory of the curated BIDS dataset.")
    return parser.parse_args()

args = parse_args()
bids_string = args.bids_string
beh_inputdir = args.beh_inputdir
bids_dir = args.bids_dir

taskname = 'task-narratives'
ses = 'ses-02'

if bids_string:
    fname = Path(bids_string).name
    sub = extract_bids(fname, 'sub')
    ses = extract_bids(fname, 'ses')
    run = re.search(r'run-\d+', fname).group(0)
    # run = extract_bids(fname, 'run')
    narrative_format2bids(sub, ses, run, taskname, beh_inputdir, bids_dir)
else:
    # If no bids_string is provided, loop through the entire directory
    file_list = sorted(glob.glob(os.path.join(beh_inputdir, '**', f'sub-*task-narratives*_beh.csv'), recursive=True))
    for fpath in file_list:
        fname = Path(fpath).name
        sub = extract_bids(fname, 'sub')
        ses = extract_bids(fname, 'ses')
        # run = extract_bids(fname, 'run')
        run = re.search(r'run-\d+', fname).group(0)
        narrative_format2bids(sub, ses, run, taskname, beh_inputdir, bids_dir)

