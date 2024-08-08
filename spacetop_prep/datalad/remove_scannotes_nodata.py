################################################################################

"""
This script deletes files in the datalad directory based on scan notes.

If a "no-data" entry is found in the scan notes, the corresponding directory in
datalad is queried. The script checks if the TR count is less than expected or
if the _bold.nii.gz file exists. It then cross-compares with empty events.tsv 
files to identify failed fMRI acquisitions. If conditions are met, related files 
are deleted to prevent the use of incomplete data.
"""

import re
import pandas as pd
from pathlib import Path
import json
import subprocess

datalad_dir = '/Users/h/Documents/projects_local/1076_spacetop'

task_mapping = {
    'T1': 'task-t1',
    'DWI': 'task-dwi',
    'Fractional': 'task-fractional',
    'PVC': 'task-social',
    'short-video': 'task-shortvideo',
    'Narratives': 'task-narratives',
    'Faces': 'task-faces',
    'Align Videos': 'task-alignvideo'
}

def extract_task_run(column_name):
    parts = column_name.split('\n')
    if len(parts) > 2:
        task_name = parts[1].strip()
        run_name = parts[2].strip().lower()
        task = task_mapping.get(task_name, 'unknown-task')
        return {"task": task, "run": run_name}
    return {"task": "unknown-task", "run": "unknown-run"}

# load st_participants

scannotes_fname = '/Users/h/Documents/projects_local/cue_expectancy/resources/spacetop_scannotes/ST_Participants - scan_info_08-10-2022.csv'
df = pd.read_csv(scannotes_fname)# load st_participants
results = []

# find the cell that has "no_data". From that, extract bids metadata (sub, ses, task, run)
for row in range(df.shape[0]):
    for col in range(df.shape[1]):
        if df.iat[row, col] == "no_data":
            # Store the coordinates
            bids_sub = df.at[row, "BIDS_id"]
            col_value = df.columns[col]
            bids_ses = df.at[row, "Session #"]
            #first_bids_sub = df.iloc[0, col]

            result = extract_task_run(col_value)
            # print(result)
            bids_task = result['task']
            bids_run = result['run']

            results.append({
                "BIDS_sub": bids_sub,
                "Column": col_value,
                "BIDS_task": bids_task,
                "BIDS_run": bids_run,
                "BIDS_ses": bids_ses
                #"First Row Value": first_bids_sub
            })

sorted_results = sorted(results, key=lambda x: x["BIDS_sub"])

TRdict = {
    "task-narratives_acq-mb8_run-01": 967,
    "task-narratives_acq-mb8_run-02": 1098,
    "task-narratives_acq-mb8_run-03": 1298,
    "task-narratives_acq-mb8_run-04": 1156,
    "task-social": 872,
    "task-fractional_acq-mb8_run-01": 1323,
    "task-fractional_acq-mb8_run-02": 1322,
    "task-shortvideo": 1616,
    "task-faces": 914,
    "ses-01_task-alignvideo_acq-mb8_run-01": 1073,
    "ses-01_task-alignvideo_acq-mb8_run-02": 1376,
    "ses-01_task-alignvideo_acq-mb8_run-03": 1016,
    "ses-01_task-alignvideo_acq-mb8_run-04": 1209,
    "ses-02_task-alignvideo_acq-mb8_run-01": 839,
    "ses-02_task-alignvideo_acq-mb8_run-02": 1859,
    "ses-02_task-alignvideo_acq-mb8_run-03": 1158,
    "ses-02_task-alignvideo_acq-mb8_run-04": 914,
    "ses-03_task-alignvideo_acq-mb8_run-01": 1157,
    "ses-03_task-alignvideo_acq-mb8_run-02": 1335,
    "ses-03_task-alignvideo_acq-mb8_run-03": 1065,
    "ses-04_task-alignvideo_acq-mb8_run-01": 1268,
    "ses-04_task-alignvideo_acq-mb8_run-02": 926
}

def TRmapper(result):
    bids_string = f"{result['BIDS_ses']}_{result['BIDS_task']}_acq-mb8_{result['BIDS_run']}"
    TR = TRdict[bids_string]
    return TR



# Run the git grep command to find empty events.tsv files. 
# This is potentially indicative of a failed MR run 
process = subprocess.Popen(['git', 'grep', '-l', 'TODO'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if process.returncode != 0:
    print(f"Error: {stderr.decode()}")
else:
    # Decode the output and filter for files ending with _event.tsv
    files = stdout.decode().splitlines()
    todo_events_list = [file for file in files if file.endswith('_event.tsv')]

    # Print the filtered file names
    for file in todo_events_list:
        print(file)


# Based on no_data basenames
for result in sorted_results:
    sub = result['BIDS_sub']
    ses = result['BIDS_ses']
    task = result['BIDS_task']
    run = result['BIDS_run']
    print(f"BIDS_sub: {result['BIDS_sub']},\n 
          Column: {result['Column']},\n, 
          BIDS_task: {result['BIDS_task']},
          BIDS_run:{result['BIDS_run']}, 
          BIDS_ses: {result['BIDS_ses']} \n\n")

    # Glob every file that matches the sorted_results basename
    bids_string = f"{sub}_{ses}_{task}_acq-mb8_{run}*"
    bids_subdir = Path(datalad_dir, sub, ses, 'func')
    matching_files = list(bids_subdir.glob(bids_string))

    #### if _bold.nii.gz does exist
    # -> check json
    # if acquisition is less than XX TR,
    # be ready to delete list of globed files first check passed

    #### check the TO and events.tsv lists that need resolving
    # if they intersect, DELETE
    # if they don't keep a tally of the non intersecting file lists. 
    # Check if _bold.nii.gz exists and perform further checks
    # For every no_data file
    for file_path in matching_files:
        # If the no_data_bold.nii.gz does exist,
        if file_path.suffix == '.nii.gz' and '_bold' in file_path.stem:
            # Check the corresponding JSON file to check the number of TRs
            json_file_path = file_path.with_suffix('.json')
            if json_file_path.exists():
                with open(json_file_path, 'r') as json_file:
                    json_data = json.load(json_file)
                    TRlength = json_data.get('dcmmeta_shape', None)[-1]
                    # if TRlength is less than expected, be ready to delete
                    expectedTR = TRmapper(results)
                    if TRlength and TRlength < expectedTR: 
                        print(f"Acquisition time is less than {expectedTR}. Ready to delete: {file_path}")

                        # Check TO and events.tsv lists
                        todo_intersect = set(todo_events_list) & set(matching_files)
                        # events_intersect = set(events_tsv_list) & set(matching_files)

                        if todo_intersect:
                            print(f"Deleting files: {matching_files}")
                            for file_to_delete in matching_files:
                                print("DELETE")
                                # file_to_delete.unlink()  # This deletes the file
                        else:
                            print(f"No intersection found. Keeping files: {matching_files}")
                    else:
                        print(f"Acquisition time is acceptable for file: {file_path}")
            else:
                print(f"JSON file does not exist for: {file_path}")
                print(f"delete all others")
                for file_to_delete in matching_files:
                    print("DELETE")
                    # file_to_delete.unlink()  # This deletes the file


# ### SCANNOTES ###
# check json
# if aquisition is less than XX TR, 
# delete all files altogether (all files with name)
# EVENTS.TSV
# cross compare this delete list with the grep TODO
# if scannote no_data and events.tsv TODO coincides, finaly delete