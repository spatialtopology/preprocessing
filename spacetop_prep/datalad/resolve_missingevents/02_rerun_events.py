import pandas as pd
from pathlib import Path
import subprocess
import os, sys

def extract_bids(filename: str, key: str) -> str:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extension, code will remove it.
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    return bids_info_rmext[0]

def run_subprocess(command: list):
    """
    Runs a subprocess command and handles any errors that occur during execution.

    Parameters:
    -----------
    command : list
        The command to run, split into list elements (e.g., ['python', 'script.py']).
    
    Returns:
    --------
    None
    """
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")

code_dir = '/Users/h/Documents/projects_local/1076_spacetop/spacetop-prep/spacetop_prep'

log_file_path = Path(code_dir) / 'datalad' / 'resolve_missingevents' / 'output_log_file.log'  # Update this path to your desired log file location
with open(log_file_path, 'w') as log_file:
    sys.stdout = log_file
    sys.stderr = log_file
    # load tsv file
    missing_fname = Path(code_dir) / 'datalad' / 'resolve_missingevents' / 'missing_events_manual_inspection.tsv'
    missing_df = pd.read_csv(missing_fname, sep='\t')

    # Define the directory of the script to run


    # Iterate over each row in the DataFrame
    for index, row in missing_df.iterrows():
        bids_string = row['BIDS_string']
        
        # BIDS extract
        bids_string = missing_df['BIDS_string']
        # sub = extract_bids(bids_string, 'sub')
        # ses = extract_bids(bids_string, 'ses')
        # run = extract_bids(bids_string, 'run')
        taskname = extract_bids(bids_string, 'taskname')
        if taskname is None:
            print(f"Task name extraction failed for index {index}. Skipping.")
            continue
        # Determine the script to run based on the task name
        script_map = {
            'task-alignvideos': 'bidsify_alignvideos_ENH.py',
            'task-faces': 'bidsify_faces_ENH.py',
            'task-fractional': 'bidsify_fractional_ENH.py',
            'task-narratives': 'bidsify_narratives_ENH.py'
        }
        script_name = script_map.get(taskname)
        if script_name is None:
            print(f"Unknown task: {taskname}. Skipping index {index} {bids_string}\n")
            continue

        script_path = Path(code_dir) / 'events' / script_name
        # Verify the script path exists
        if not script_path.is_file():
            print(f"Script {script_path} not found. Skipping index {index} {bids_string}\n")
            continue

        command = ['python', str(script_path), '--bids_string', bids_string,  ]
        print(f"Running command for index {index}: {bids_string} {command}")
        run_subprocess(command)
        print(f"Complete\n")

    # Reset stdout and stderr back to default
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
