import os, re, glob
import pandas as pd
import numpy as np
import argparse
from pathlib import Path

"""
# Generate events files for task-alignvideo
# This script reads raw behavior data files from d_beh for task-alignvideo, extracts time stamps and design information, and stores them in new *events.tsv files accompanying BOLD files.
# For more information, please see README.md and the associated paper (Jung et al., 2024)
"""
def extract_bids(filename: str, key: str) -> str:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extension, code will remove it.
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    return bids_info_rmext[0]
def add_rating_event(source_beh, t, t_run_start, rating_type, event_onset, event_rt, response_value_column):
    """
    Adds a rating event to the new BIDS-compliant DataFrame.

    Parameters:
    -----------
    source_beh : DataFrame
        The source behavioral data.
    t : int
        The trial index.
    t_run_start : float
        The start time of the run.
    rating_type : str
        The type of rating event.
    event_onset : str
        The onset column name in the source data.
    event_rt : str
        The reaction time column name in the source data.
    response_value_column : str
        The response value column name in the source data.

    Returns:
    --------
    DataFrame
        A DataFrame containing the formatted event.
    """
    onset = source_beh.loc[t, event_onset] - t_run_start
    duration = source_beh.loc[t, event_rt]
    response_value = source_beh.loc[t, response_value_column]
    if duration == 0:
        duration = np.nan
        response_value = np.nan
    return pd.DataFrame({
        "onset": onset, "duration": duration, "trial_type": rating_type, 
        "response_value": response_value, "stim_file": source_beh.loc[t, 'param_video_filename']
    }, index=[0])

def alignvideo_format_to_bids(sub, ses, run, task_name, beh_inputdir, bids_dir):
    """
    Converts behavioral data from a raw format to a BIDS-compliant events.tsv file for a specific task.

    This function reads raw behavioral data files, extracts time stamps and event information, and formats 
    them into a BIDS-compatible events.tsv file. The function handles various types of events (e.g., video 
    presentation, ratings) and computes relevant onset and duration times, adjusting for the start time of the run.

    Parameters:
    -----------
    sub : str
        The subject identifier (e.g., 'sub-0001').
    ses : str
        The session identifier (e.g., 'ses-01').
    run : str
        The run identifier (e.g., 'run-01').
    task_name : str
        The task name (e.g., 'task-alignvideos').
    beh_inputdir : str
        The directory path where the raw behavioral data files are located.
    bids_dir : str
        The root directory of the BIDS dataset where the formatted events.tsv files will be saved.

    Returns:
    --------
    None. Saves data to a new .tsv file in bids_dir

    Notes:
    ------
    - If the specified behavioral data file does not exist, the function prints a message and exits.
    - The function creates an events.tsv file with the following columns: onset, duration, trial_type, 
      response_value, stim_file.
    - Each event type (video presentation, different ratings) is processed separately and added to the 
      events.tsv file.
    - If a rating duration is 0 (indicating no response), the duration and response value are set to NaN 
      and later replaced with "n/a".
    - The resulting events.tsv file is saved with 3 decimal places for onset and duration, and 2 decimal 
      places for response values.
    
    Raises:
    -------
    IOError:
        If there is an error saving the resulting events.tsv file.

    Example:
    --------
    format2bids('sub-0001', 'ses-01', 'run-01', 'task-alignvideos', '/path/to/beh_data', '/path/to/bids_data')
    """
    fpath = Path(beh_inputdir) / sub / 'task-alignvideos' / ses / f'{sub}_{ses}_task-alignvideos_{run}_beh.csv'
    if not fpath.is_file():
        # Attempt to find a temporary or alternative file
        temp_fpath = Path(beh_inputdir) / sub / 'task-alignvideos' / ses / f'{sub}_{ses}_task-alignvideo*{run}*TEMP*.csv'
        
        if temp_fpath.is_file():
            fpath = temp_fpath
        else:
            print(f'No behavior data file found for {sub}, {ses}, {run}. Checked both standard and temporary filenames.')
            return
        
    source_beh = pd.read_csv(fpath)
    new_beh = pd.DataFrame(columns=["onset", "duration", "trial_type", 
                            "response_value", "stim_file"])    # new events to store

    t_run_start = source_beh.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

    for t in range(len(source_beh)):    # each trial
        # Event 1. stimuli presentation
        onset = source_beh.loc[t, 'event01_video_onset'] - t_run_start
        duration = source_beh.loc[t, 'event01_video_end'] - source_beh.loc[t, 'event01_video_onset']
        trial_type = 'video'
        stim_file = task_name + '/' + source_beh.loc[t, 'param_video_filename']
        new_row = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                        "stim_file": stim_file}, index=[0])
        new_beh = pd.concat([new_beh, new_row], ignore_index=True)

        # Event 2 through Event 8. Seven Emotion Ratings
        new_beh = pd.concat([
            new_beh,
            add_rating_event(source_beh, t, t_run_start, 'rating_relevance', 'event02_rating01_onset', 'event02_rating01_RT', 'event02_rating01_rating'),
            add_rating_event(source_beh, t, t_run_start, 'rating_happy', 'event02_rating02_onset', 'event02_rating02_RT', 'event02_rating02_rating'),
            add_rating_event(source_beh, t, t_run_start, 'rating_sad', 'event02_rating03_onset', 'event02_rating03_RT', 'event02_rating03_rating'),
            add_rating_event(source_beh, t, t_run_start, 'rating_afraid', 'event02_rating04_onset', 'event02_rating04_RT', 'event02_rating04_rating'),
            add_rating_event(source_beh, t, t_run_start, 'rating_disgusted', 'event02_rating05_onset', 'event02_rating05_RT', 'event02_rating05_rating'),
            add_rating_event(source_beh, t, t_run_start, 'rating_warm', 'event02_rating06_onset', 'event02_rating06_RT', 'event02_rating06_rating'),
            add_rating_event(source_beh, t, t_run_start, 'rating_engaged', 'event02_rating07_onset', 'event02_rating07_RT', 'event02_rating07_rating')
        ], ignore_index=True)

    # change precisions
    precision_dic = {'onset': 3, 'duration': 3, 'response_value': 2}
    new_beh = new_beh.round(precision_dic)
    new_beh = new_beh.replace(np.nan, 'n/a') # replace nan with "n/a" in BIDS way
    # Save new events file
    try:
        new_fname = Path(bids_dir) / sub / ses / 'func' / f'{sub}_{ses}_{task_name}_acq-mb8_{run}_events.tsv'
        new_beh.to_csv(new_fname, sep='\t', index=False)
    except OSError as e:
        print(f"Failed to save {sub} {ses} {task_name} {run}: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Process behavioral files for specific subjects or all subjects.")
    parser.add_argument('--bids_string', type=str, help="BIDS formatted string in format: sub-{sub%04d}_ses-{ses%02d}_task-{task}_run-{run%02d}")
    parser.add_argument('--bids_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop', help="Curated top directory of datalad.")
    parser.add_argument('--source_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop/sourcedata', help="Where the source behavioral directory lives.")
    return parser.parse_args()

# %% ---------------------------------------------------------------------------
#  1.  parameters
# ------------------------------------------------------------------------------

args = parse_args()
bids_string = args.bids_string
bids_dir = args.bids_dir
source_dir = args.source_dir
beh_inputdir = Path(source_dir) / 'd_beh'

task_name = 'task-alignvideo'
session_dict = {'ses-01': 4, 'ses-02': 4, 'ses-03': 3, 'ses-04': 2} # NOTE: different sessions have different numbers of runs

if bids_string:
    fname = Path(bids_string).name
    sub = extract_bids(fname, 'sub')
    ses = extract_bids(fname, 'ses')
    run = extract_bids(fname, 'run')
    alignvideo_format_to_bids(sub, ses, run, task_name, beh_inputdir, bids_dir)
else:
    # If no bids_string is provided, loop through the entire directory
    folders = glob.glob(os.path.join(bids_dir, 'sub-*'))
    sub_list = [os.path.basename(x) for x in folders]
    for sub in sorted(sub_list):
        for ses in session_dict:
            for run_index in range(session_dict[ses]):
                run = f'run-0{run_index+1}'
                alignvideo_format_to_bids(sub, ses, run, task_name, beh_inputdir, bids_dir)