"""
purpose of this file
remove filenames with __dup from the IntendedFor and the scans.tsv
"""
# 1. git annex unlock scans.tsv
# 1-1. delete row of __dup file from scans.tsv
# 1-2. git lock scans.tsv

# 2. git annex unlock .json
# 2-1. delete item of __dup from .json
# 2-2. need to handle list of items (commas?)

import pandas as pd
import json
import subprocess
import os, glob

def remove_dup_files(scans_tsv_path, json_dir):
    # Step 1: Unlock scans.tsv
    subprocess.run(["git", "annex", "unlock", scans_tsv_path])

    # Step 1-1: Delete rows with __dup files from scans.tsv
    scans_df = pd.read_csv(scans_tsv_path, sep='\t', header=None, names=['filename'])
    scans_df = scans_df[~scans_df['filename'].str.contains('__dup')]
    scans_df.to_csv(scans_tsv_path, sep='\t', header=False, index=False)

    # Step 1-2: Lock scans.tsv
    subprocess.run(["git", "annex", "lock", scans_tsv_path])

    # Step 2: Unlock all .json files in the specified directory
    for json_file in os.listdir(json_dir):
        if json_file.endswith('.json'):
            json_file_path = os.path.join(json_dir, json_file)
            subprocess.run(["git", "annex", "unlock", json_file_path])

            # Step 2-1: Delete items with __dup from .json files
            with open(json_file_path, 'r+') as f:
                data = json.load(f)
                if 'IntendedFor' in data:
                    intended_for_list = data['IntendedFor']
                    intended_for_list = [item for item in intended_for_list if '__dup' not in item]
                    data['IntendedFor'] = intended_for_list
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

            # Step 2-2: Handle lists of items (commas in this case are naturally handled by JSON)
            subprocess.run(["git", "annex", "lock", json_file_path])


import pandas as pd
import subprocess

def edit_scans_tsv(scans_tsv_path):
    # Unlock scans.tsv
    subprocess.run(["git", "annex", "unlock", scans_tsv_path])

    # Read the scans.tsv file into a DataFrame
    scans_df = pd.read_csv(scans_tsv_path, sep='\t', header=None, names=['filename'])

    # Delete rows with __dup files
    scans_df = scans_df[~scans_df['filename'].str.contains('__dup')]

    # Save the updated DataFrame back to scans.tsv
    scans_df.to_csv(scans_tsv_path, sep='\t', header=False, index=False)

    # Lock scans.tsv
    subprocess.run(["git", "annex", "lock", scans_tsv_path])

import json
import os

def edit_json_files(json_dir):
    # Iterate over all .json files in the specified directory
    for json_file in os.listdir(json_dir):
        if json_file.endswith('.json'):
            json_file_path = os.path.join(json_dir, json_file)

            # Unlock the json file
            subprocess.run(["git", "annex", "unlock", json_file_path])

            # Read and update the JSON file
            with open(json_file_path, 'r+') as f:
                data = json.load(f)
                if 'IntendedFor' in data:
                    intended_for_list = data['IntendedFor']
                    # Delete items with __dup from the IntendedFor list
                    intended_for_list = [item for item in intended_for_list if '__dup' not in item]
                    data['IntendedFor'] = intended_for_list

                    # Write the updated JSON back to the file
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

            # Lock the json file
            subprocess.run(["git", "annex", "lock", json_file_path])


def main():
    base_dir = 'path/to/base/directory'

    # Walk through the base directory to find and process scans.tsv files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if 'scans.tsv' in file:
                scans_tsv_path = os.path.join(root, file)
                edit_scans_tsv(scans_tsv_path)

    # Process all .json files in the base directory and its subdirectories
    edit_json_files(base_dir)

if __name__ == "__main__":
    main()

json_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth'
def check_dup_in_intendedfor(json_dir):
    count_dup_files = 0
    total_files_checked = 0

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(json_dir):
        for json_file in files:
            if json_file.endswith('.json'):
                json_file_path = os.path.join(root, json_file)
                total_files_checked += 1

                # Read the JSON file
                with open(json_file_path, 'r') as f:
                    try:
                        data = json.load(f)
                        if 'IntendedFor' in data:
                            intended_for_list = data['IntendedFor']
                            # Check for items with __dup in the IntendedFor list
                            if any('__dup' in item for item in intended_for_list):
                                count_dup_files += 1
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {json_file_path}")

    return count_dup_files, total_files_checked
