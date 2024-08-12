"""
Based on manual observation of scannotes and datalad
(after `datalad/delete_func_scannotes/01_remove_scannotes_nodata.py` and 
`datalad/delete_func_scannotes/delete_bold.tsv`), we have a final list of files 
to delete. In this code, we delete funcs and keep ones that require further investigation or false alarms.

* If HJ_manualdecision column is "delete" identify all files with corresponding BIDS_string, then delete

"""
import os, re
import pandas as pd
# read .tsv
df = pd.read_csv('datalad/delete_func_scannotes/delete_bold.tsv')

# if  HJ_manualdecision column ['HJ_manualdecision'] == 'delete'
# grab the BIDS_string in that corresponding row
# identify all files that match the BIDS_string
# delete altogether


# Load the .tsv file into a DataFrame
df = pd.read_csv('datalad/delete_func_scannotes/delete_bold.tsv', sep='\t')

# Filter rows where the 'HJ_manualdecision' column is 'delete'
to_delete = df[df['HJ_manualdecision'] == 'delete']

# Iterate through the rows in the filtered DataFrame
for index, row in to_delete.iterrows():
    # Get the BIDS_string from the current row
    bids_string = row['BIDS_string']
    pattern = r"sub-(?P<sub>[^_]+)_ses-(?P<ses>[^_]+)_task-(?P<task>[^_]+).*_run-(?P<run>[^_]+)"

    # Search for the pattern in the BIDS string
    match = re.search(pattern, bids_string)

    # If a match is found, extract the values
    if match:
        sub = match.group('sub')
        ses = match.group('ses')
        task = match.group('task')
        run = match.group('run')
        
        print(f"sub = '{sub}'")
        print(f"ses = '{ses}'")
        print(f"task = '{task}'")
        print(f"run = '{run}'")
    else:
        print("No match found")
    # Find all files that match the BIDS_string pattern
    # Assuming these files are located in a directory structure matching the BIDS format
    # and that BIDS_string corresponds to a unique part of the file path
    for root, dirs, files in os.walk('/Users/h/Documents/projects_local/1076_spacetop'):
        for file in files:
            if bids_string in file:
                # Construct the full path to the file
                file_path = os.path.join(root, file)
                
                # Delete the file
                os.remove(file_path)
                print(f"Deleted: {file_path}")

print("Deletion process completed.")
