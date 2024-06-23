#!/usr/bin/env python
"""
Remove "desc" keyword and add metadata into scans tsv
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

# Configure the logger globally
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""
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
        if 'task-fractional' in file and file.endswith('.nii.gz'):
            nifti_files.append(file)
        elif 'task-fractional' in file and file.endswith('_events.tsv'):
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


def extract_metadata_and_run(filename):
    cue_metadata = re.search(r'_desc-(\w+)_events\.tsv', filename).group(1)
    run = re.search(r'_run-(\d+)_', filename).group(1)
    return cue_metadata, run

# Function to extract run information from filenames
def extract_run(filename):
    match = re.search(r'_run-(\d+)_', filename)
    return match.group(1) if match else None

# Function to map fractional files to cue metadata
def map_fractional_to_cue(filename):
    run = extract_run(filename)
    if run in fractional_metadata_dict:
        return fractional_metadata_dict[run]
    return None

def is_equivalent(val1, val2, tolerance=1):
    return abs(val1 - val2) <= tolerance
# TODO:



def is_equivalent(val1, val2, tolerance=1):
    return abs(val1 - val2) <= tolerance

# %% ---------------------------------------------------------------------------
#  1. add task-fractional runtype metadata & 2. harmonize scans tsv and nifti files
# ------------------------------------------------------------------------------


scans_list = sorted(glob.glob('sub-*/**/*ses-04*scans*.tsv', recursive=True))
for scan_fname in scans_list:
    # NOTE: Step 1: Get the scans.tsv using datalad
    run_command(f"datalad get {scan_fname}")
    print(f"datalad get {scan_fname} ")
    # Check if scans_file is not empty and unlock it using git annex
    if os.path.exists(scan_fname) and os.path.getsize(scan_fname) > 0:
        run_command(f"git annex unlock {scan_fname}")
        print(f"Step 1: unlock {scan_fname}")

    scans_df = pd.read_csv(scan_fname, sep='\t')

    # NOTE: Step 2: Define the directory containing the task-cue event files
    fractional_events_dir = './' + os.path.dirname(scan_fname) + '/func'
    fractional_events_files = sorted([f for f in os.listdir(fractional_events_dir) if 'task-fractional' in f and f.endswith('_events.tsv') and 'desc-' in f])
    print("Step 2:")
    # NOTE: Step 3: Function to extract cue metadata and run information from filenames
    # Create a dictionary to map run to cue metadata
    fractional_metadata_dict = {}
    for file in fractional_events_files:
        metadata, run = extract_metadata_and_run(file)
        fractional_metadata_dict[run] = metadata
    print("")


    # NOTE: Step 4: Apply the function to add the task-fractional_runtype column

    mask = scans_df['filename'].str.contains('task-fractional')
    scans_df.loc[mask, 'task-fractional_runtype'] = scans_df.loc[mask, 'filename'].apply(map_fractional_to_cue)

    scans_df['task-fractional_runtype'].fillna("n/a", inplace=True)


    # NOTE: Step 5: if events file and niftifiles disagree, delete files
    nifti_files, event_files = list_nifti_and_event_files(fractional_events_dir)
    orphan_files = remove_orphan_nifti_files(nifti_files, event_files)
    if orphan_files:
        for orphan_file in orphan_files:
            print(f"Removing {orphan_file}")
            run_command(f"git rm {orphan_file}")
            scans_df = scans_df[scans_df['filename'] != os.path.basename(orphan_file)]

    scans_df.to_csv(scan_fname, index=False)

    # Add the updated scans_file back to git annex
    print(f"made edits to events file and deleted nifti files if not harmonized: {scan_fname}")
    run_command(f"git annex add {scan_fname}")



    # NOTE: Step 6: rename file events files
    # NOTE: Step 6: ultimately, delete BIDS data
    for event_fname in fractional_events_files:
        event_fpath = os.path.join(fractional_events_dir, event_fname)
        keyword = event_fpath.split("desc-")[1].split("_events")[0] # extract subtask keyword e.g. posner, tomsaxe
        df = pd.read_csv(event_fpath, sep='\t')
        df.insert(2, 'subtask_type', keyword) # Insert new column called 'subtask_type' with extracted keyword
        df.to_csv(event_fpath, sep='\t', index=False) 
        new_event_fpath = event_fpath.replace(f"_desc-{keyword}", "") # Rename the event_fpath to drop the "_desc-keyword"
        os.rename(event_fpath, new_event_fpath)
        run_command(f"git annex add {new_event_fpath}")
        run_command(f"git rm {event_fpath}")
        print(f"remove all the task-cue events files {event_fpath}")

        # Add the updated scans_file back to git annex
        print(f"made edits to events file and deleted nifti files if not harmonized: {scan_fname}")

      


run_command(f"git commit -m 'DOC: update scans tsv with task-fractional runtype metadata and remove orphan NIfTI files delete non-bids compliant events file'")