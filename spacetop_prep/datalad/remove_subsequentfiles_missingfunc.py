import os
import glob

datalad_dir = '/Users/h/Documents/projects_local/1076)spacetop'
# Define the suffixes for the different file types
file_suffixes = ['_bold.json', '_bold.nii.gz', '_events.tsv', '_sbref.json', '_sbref.nii.gz']

# List all files in the current directory

folders = glob.glob(os.path.join(datalad_dir, 'sub-*'))
sublist = sorted([os.path.basename(x) for x in folders])

for sub in sublist:

    files = glob.glob(os.path.join(datalad_dir, sub, '*'))

    # Dictionary to keep track of files grouped by their base name
    file_dict = {}

    for file in files:
        # Strip .gz if present
        base_name, suffix = os.path.splitext(file)
        if suffix == '.gz':
            base_name, _ = os.path.splitext(base_name)  # remove the .gz suffix

        # Determine the base name
        for suffix in file_suffixes:
            if file.endswith(suffix):
                base_name = file[:-len(suffix)]  # remove the suffix
                break

        # Group files by their base name
        if base_name not in file_dict:
            file_dict[base_name] = []
        file_dict[base_name].append(file)

    # Process each base name group
    for base_name, file_list in file_dict.items():
        # Check if _bold.nii.gz exists
        bold_nifti_exists = any(f.endswith('_bold.nii.gz') for f in file_list)
        
        if not bold_nifti_exists:
            # If no _bold.nii.gz file exists, remove all files in this group
            for file in file_list:
                print(f"Removing file: {file}")
                os.remove(file)

    print("Cleanup completed.")


import re
import pandas as pd


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




import pandas as pd
# load st_participants
# find the cell that has "no_data" -> extract sub, ses, task
# from that, remove all files that have string {sub}_{ses}_{task}_{run}
scannotes_fname = '/Users/h/Documents/projects_local/cue_expectancy/resources/spacetop_scannotes/ST_Participants - scan_info_08-10-2022.csv'
df = pd.read_csv(scannotes_fname)# load st_participants
results = []


# Iterate over each cell to find "no_data"
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
            task = result['task']
            run = result['run']

            results.append({
                "BIDS_sub": bids_sub,
                "Column": col_value,
                "BIDS_task": task,
                "BIDS_run": run,
                "BIDS_ses": bids_ses
                #"First Row Value": first_bids_sub
            })

sorted_results = sorted(results, key=lambda x: x["BIDS_sub"])

# Display the results
for result in sorted_results:
    print(f"BIDS_sub: {result['BIDS_sub']},\n Column: {result['Column']},\n, BIDS_task: {result['BIDS_task']},BIDS_run:{result['BIDS_run']}, BIDS_ses: {result['BIDS_ses']} \n\n")

# SCANNOTES
# check json
# if aquisition is less than XX TR, 
# delete all files altogether (all files with name)
# EVENTS.TSV
# cross compare this delete list with the grep TODO
# if scannote no_data and events.tsv TODO coincides, finaly delete