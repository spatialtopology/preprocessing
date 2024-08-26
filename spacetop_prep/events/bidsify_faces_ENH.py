# Generate events files for task-faces

# This script reads raw behavior data files from d_beh for task-faces, extracts time stamps and design information, and stores them in new *events.tsv files accompanying BOLD files.

# For more information, please see README.md and the associated paper (Jung et al., 2024)

import os, glob
import pandas as pd
import numpy as np
import argparse
from pathlib import Path

def extract_bids(filename: str, key: str) -> str:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extension, code will remove it.
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    return bids_info_rmext[0]

def load_data_file(sub, ses, taskname, run, rating_type, beh_inputdir):
    beh_fname_pattern = str(beh_inputdir / sub / taskname / f'{sub}_{ses}_{taskname}_{run}-{rating_type}_beh-preproc.csv')
    matching_files = glob.glob(beh_fname_pattern)
    
    if matching_files:
        beh_fname = Path(matching_files[0])
    else:
        # Check for the non-preproc file
        beh_fname = Path(beh_inputdir) / sub / taskname / f'{sub}_{ses}_{taskname}_{run}_beh.csv'
        
        if not beh_fname.is_file():
            # Attempt to find a temporary or alternative file
            temp_pattern = str(Path(beh_inputdir) / sub / taskname / ses / f'{sub}_{ses}_{taskname}*{run}*TEMP*.csv')
            temp_files = glob.glob(temp_pattern)
            
            if temp_files:
                beh_fname = Path(temp_files[0])
            else:
                print(f'No behavior data file found for {sub}, {ses}, {run}. Checked both standard and temporary filenames.')
                return None
    return pd.read_csv(beh_fname)
    

def process_trial_data(source_beh, run, rating_type):
    new_beh = pd.DataFrame(columns=["onset", "duration", "trial_type", "response_value", 
                                    "rating_type", "expression", "sex", "race", "age", "stim_file"])
    t_runstart = source_beh.loc[0, 'param_trigger_onset']
    
    for t in range(len(source_beh)):
        trial_data = format_behavioral_data(source_beh, t, t_runstart, rating_type) #run_dict[run])
        new_beh = pd.concat([new_beh, trial_data], ignore_index=True)

    return new_beh

def format_behavioral_data(source_beh, trial_index, t_runstart, rating_type):
    new_beh = pd.DataFrame()

    # Extract common data
    conditions = source_beh.loc[trial_index, 'param_video_filename'].split('_')
    expression = conditions[0][1:].lower()
    sex = conditions[2][1:].lower()
    race = conditions[3][1:]
    age = conditions[4][1:-4].lower()

    # Event 1. face video playing
    onset = source_beh.loc[trial_index, 'event02_face_onset'] - t_runstart
    duration = source_beh.loc[trial_index, 'event03_rating_displayonset'] - source_beh.loc[trial_index, 'event02_face_onset']
    trial_type = 'face'
    stim_file = f"task-faces/{source_beh.loc[trial_index, 'param_video_filename']}"
    newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type,
                           "rating_type": rating_type, 'expression': expression, 'sex': sex,
                           "race": race, "age": age, 'stim_file': stim_file}, index=[0])
    new_beh = pd.concat([new_beh, newRow], ignore_index=True)

    # Event 2. rating
    onset = source_beh.loc[trial_index, 'event03_rating_displayonset'] - t_runstart
    # duration = source_beh.loc[trial_index, 'event03_rating_RT'] if ~np.isnan(source_beh.loc[trial_index, 'event03_rating_RT']) else source_beh.loc[trial_index, 'RT_adj']
    duration = source_beh.loc[trial_index, 'event03_rating_RT'] if pd.notna(source_beh.loc[trial_index, 'event03_rating_RT']) else source_beh.loc[trial_index, 'RT_adj']

    trial_type = 'rating'
    if 'rating_converted' in source_beh.columns:
        response_value = source_beh.loc[trial_index, 'rating_converted']
    else:
        response_value = 'n/a'
    newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type,
                           "response_value": response_value, "rating_type": rating_type,
                           'expression': expression, 'sex': sex, "race": race, "age": age}, index=[0])
    new_beh = pd.concat([new_beh, newRow], ignore_index=True)

    # Event 3. rating mouse trajectory
    if 'motion_onset' in source_beh.columns:
        onset += source_beh.loc[trial_index, 'motion_onset']
        duration = source_beh.loc[trial_index, 'motion_dur']
    else:
        onset = 'n/a'
        duration = 'n/a'  # Or some default value if neither column exists

    # onset += source_beh.loc[trial_index, 'motion_onset']
    # duration = source_beh.loc[trial_index, 'motion_dur']
    trial_type = 'rating_mouse_trajectory'
    newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type,
                           "response_value": response_value, "rating_type": rating_type,
                           'expression': expression, 'sex': sex, "race": race, "age": age}, index=[0])
    new_beh = pd.concat([new_beh, newRow], ignore_index=True)

    return new_beh

def save_events_file(new_beh, bids_dir, sub, ses, taskname, run):
    precision_dic = {'onset': 3, 'duration': 3, 'response_value': 4}
    new_beh = new_beh.round(precision_dic)
    
    new_beh = new_beh.replace(np.nan, 'n/a') # replace missing values the BIDS way
    new_fname = Path(bids_dir) / sub / ses / 'func' / f'{sub}_{ses}_{taskname}_acq-mb8_{run}_events.tsv'
    try:
        new_beh.to_csv(new_fname, sep='\t', index=False)
    except Exception as e:
        print(f"Error saving file {new_fname}: {e}")

def faces_format2bids(sub, ses, taskname, run, rating_type, beh_inputdir, bids_dir):
    source_beh = load_data_file(sub, ses, taskname, run, rating_type, beh_inputdir)
    if source_beh is not None:
        new_beh = process_trial_data(source_beh, run, rating_type) #def process_trial_data(source_beh, run, rating_type):
        save_events_file(new_beh, bids_dir, sub, ses, taskname, run)


def parse_args():
    parser = argparse.ArgumentParser(description="Process behavioral files for specific subjects or all subjects.")
    parser.add_argument('--bids_string', type=str, help="BIDS formatted string in format: sub-{sub%04d}_ses-{ses%02d}_task-{task}_run-{run%02d}")
    parser.add_argument('--bids_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop', help="Curated top directory of datalad.")
    parser.add_argument('--source_dir', type=str, default='/Users/h/Documents/projects_local/1076_spacetop/sourcedata', help="Where the source behavioral directory lives.")
    return parser.parse_args()


def main():
    args = parse_args()
    bids_string = args.bids_string
    bids_dir = Path(args.bids_dir)
    beh_inputdir = Path(args.source_dir) / 'd_beh'
    
    ses = 'ses-02'
    taskname = 'task-faces'
    
    if bids_string:
        fname = Path(bids_string).name
        sub = extract_bids(fname, 'sub')
        ses = extract_bids(fname, 'ses')
        run = extract_bids(fname, 'run')
        run_dict = {'run-01': 'age', 'run-02': 'sex', 'run-03': 'intensity'} if int(sub[-4:])%2 == 0 else {'run-01': 'intensity', 'run-02': 'sex', 'run-03': 'age'}
        rating_type = run_dict[run]
        faces_format2bids(sub, ses, taskname, run, rating_type, beh_inputdir, bids_dir)
    else:

        faces_flist = glob.glob(str(beh_inputdir / '**' / f'*task-faces*.csv'), recursive=True)
        filtered_faces_flist = [file for file in faces_flist if "sub-0001" not in file]
        
        for fpath in sorted(filtered_faces_flist):
            fname = Path(fpath).name
            sub = extract_bids(fname, 'sub')
            ses = extract_bids(fname, 'ses')
            run = extract_bids(fname, 'run')
            run_dict = {'run-01': 'age', 'run-02': 'sex', 'run-03': 'intensity'} if int(sub[-4:])%2 == 0 else {'run-01': 'intensity', 'run-02': 'sex', 'run-03': 'age'}
            rating_type = run_dict[run]
            faces_format2bids(sub, ses, taskname, run, rating_type, beh_inputdir, bids_dir)

if __name__ == "__main__":
    main()
