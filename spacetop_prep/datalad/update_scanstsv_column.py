"""
Resolve error that scans.tsv does not have corresponding BIDS column
"""
import os, glob
import json
from pathlib import Path
import subprocess
import pandas as pd
datalad_dir = '/Users/h/Documents/projects_local/1076_spacetop'
# for * ses-01, ses-02, ses-03 * .json files, update column "task-social_runtype"
sessions = ['01', '02', '03']
for session in sessions:
    session_path = Path(datalad_dir) / '**' / f'ses-{session}' / f'*_ses-{session}_scans.json'
    files = glob.glob(str(session_path), recursive=True)
    for file in files:
        subprocess.run(["git", "annex", "unlock", file])
        with open(file, 'r+') as f:
            data = json.load(f)
            data["task-social_runtype"] = {
                "LongName": "Runtype of task-social runs",
                "Description": "Runtype of task-social runs. Options: ['pain', 'vicarious', 'cognitive']"
            }
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        subprocess.run(["git", "annex", "lock", file])



# for * ses-04, update column task-social_runtype,task-fractional_runtype
session_path = Path(datalad_dir) / '**' / f'ses-04' / f'*_ses-04_scans.json'
files = glob.glob(str(session_path), recursive=True)
for file in files:
    subprocess.run(["git", "annex", "unlock", file])
    with open(file, 'r+') as f:
        data = json.load(f)
        data["task-social_runtype"] = data["task-social_runtype"] = {
                "LongName": "Runtype of task-social runs",
                "Description": "Runtype of task-social runs. Options: ['pain', 'vicarious', 'cognitive']"
            }
        data["task-fractional_runtype"] = {
                "LongName": "Runtype of task-social runs",
                "Description": "Runtype of task-fractional runs. Options: ['tomsaxe', 'tomspunt', 'memory', 'posner']"}
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    subprocess.run(["git", "annex", "lock", file])

    # Step 1: Unlock scans.tsv

session_path = Path(datalad_dir) / '**' / f'ses-04' / f'*_ses-04_scans.tsv'
files = glob.glob(str(session_path), recursive=True)
for file in files:
    subprocess.run(["git", "annex", "unlock", file])
    scans_df = pd.read_csv(file)
    scans_df.fillna("n/a")
    scans_df.to_csv(file, sep='\t', header=True, index=False)
    subprocess.run(["git", "annex", "lock", file])