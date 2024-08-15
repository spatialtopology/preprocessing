
"""
In cases where a BOLD file exists but the corresponding events.tsv file is missing, 
there are several scenarios to consider:

1. Incomplete Behavioral Data with TEMP Files Available:
TEMP files, which are trial-by-trial backups that don't rely on a final "save," 
may exist even if the behavioral data wasn't fully collected. In this case, copy 
these TEMP files into the d_beh directory and convert them into BIDS format.

2. Complete Behavioral Data, but Not BIDS Transformed:
If the behavioral data was fully collected but wasn't converted to BIDS format, 
rerun the events_to_BIDS conversion and troubleshoot any errors that arise during the process.

3. Typo in Subject ID:
A typo in the subject ID might cause the events.tsv file to be missing. After 
correcting the typo, reconvert the data into BIDS format.

4. No Behavioral Data Available:
If no behavioral data is available, make an executive decision on whether the BOLD 
data can be analyzed without the events file:
* If timing data is necessary (e.g., trials include jitter), discard the data.
* If timing data is fixed (e.g., aligned videos or narratives), the BOLD data can still be included in the analysis.

"""
# %%
import os
import subprocess
import glob
import pandas as pd

def extract_bids(filename: str, key: str) -> str:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extension, code will remove it.
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    return bids_info_rmext[0]

def c1_process_temp_files(sub, ses, task, run, repo2task_dict):
    """
    Processes and copies TEMP files based on task and run information.
    """
    base_path = f"~/repos/{repo2task_dict.get(task, '')}/data/{sub}/{ses}/beh"
    
    # Adjust paths and patterns based on task type
    if task == "task-shortvideos":
        base_path = f"~/repos/{repo2task_dict[task]}/data/{sub}/ses-03/beh"
    elif task == "task-faces":
        base_path = f"~/repos/{repo2task_dict[task]}/data/{sub}/beh/ses-02"
    elif task == "task-narratives":
        base_path = f"~/repos/{repo2task_dict[task]}/data/{sub}/beh/"
    
    file_pattern = f"{sub}*{ses}*{task}*{run}*TEMP*beh.csv" if task in ["task-alginvideo", "task-social"] else f"{sub}*{task}*TEMP*beh.csv"
    
    os.chdir(os.path.expanduser(base_path))
    for file in glob.glob(file_pattern):
        destination = f"~/repos/data/{sub}/{task}/{ses}/{sub}_{ses}_{task}_{run}_beh_TEMP.csv"
        subprocess.run(["cp", file, os.path.expanduser(destination)])
        subprocess.run(["git", "add", os.path.expanduser(destination)])
        subprocess.run(["git", "commit", "-m", "DOC: copy over temporary data"])

def c3_handle_typo_cases(typo_fname, corrected_subject_id=None, dest_fname=None, update_session_id=False):
    """
    Handles file renaming and BIDS adjustments for typo cases.
    
    Parameters:
    typo_fname (str): The path to the file with a typo.
    corrected_subject_id (str, optional): The correct subject ID. If provided, updates the 'src_subject_id' column.
    dest_fname (str, optional): The new filename if the file needs to be renamed.
    update_session_id (bool, optional): If True, updates the 'session_id' column based on the corrected filename.
    """
    # Rename the file if dest_fname is provided
    if dest_fname:
        subprocess.run(["mv", typo_fname, dest_fname])
        typo_fname = dest_fname
    
    # Load the file into a DataFrame
    typodf = pd.read_csv(typo_fname)
    
    # Update the 'src_subject_id' column if corrected_subject_id is provided
    if corrected_subject_id:
        typodf['src_subject_id'] = corrected_subject_id
    
    # Update the 'session_id' column if required
    if update_session_id and 'session_id' in typodf.columns:
        # Extract the session ID from the filename or corrected subject ID
        session_id = dest_fname.split('ses-')[1].split('_')[0] if dest_fname else corrected_subject_id.split('-')[-1]
        typodf['session_id'] = session_id
    
    # Save the updated DataFrame back to the file
    typodf.to_csv(typo_fname, index=False)
    
    # Add the file to Git and commit the changes
    subprocess.run(["git", "add", os.path.expanduser(typo_fname)])
    subprocess.run(["git", "commit", "-m", "BUG: resolve typo and update BIDS fields"])

# Load the TSV file into a DataFrame
df = pd.read_csv('./missing_events_manual_inspection.tsv', sep='\t')

# Define a dictionary for repo2task mapping
repo2task_dict = {
    "task-alginvideo": "alignvideo_repo",
    "task-social": "social_repo",
    "task-faces": "faces_repo",
    "task-narratives": "narratives_repo",
    "task-shortvideos": "shortvideos_repo"
}

for _, row in df.iterrows():
    sub = extract_bids(row['BIDS_string'], 'sub')
    ses = extract_bids(row['BIDS_string'], 'ses')
    run = extract_bids(row['BIDS_string'], 'run')
    task = extract_bids(row['BIDS_string'], 'task')

    if row['case'] == 'C1':
        # if case 1, copy over TEMP files from git repo
        c1_process_temp_files(sub, ses, task, run, repo2task_dict)
    
    elif row['case'] == 'C3':
        c3_handle_typo_cases('./d_beh/sub-0016/task-alignvideos/ses-04/sub-0156_ses-04_task-alignvideos_run-01_TEMP_beh.csv', 
                             corrected_subject_id=16, 
                             dest_fname="./d_beh/sub-0016/task-alignvideos/ses-04/sub-0016_ses-04_task-alignvideos_run-01_TEMP_beh.csv",update_session_id=True)
        
        typo_flist = ['sub-0021/ses-01/func/sub-0021_ses-01_task-social_acq-mb8_run-01_events.tsv',
        'sub-0021/ses-01/func/sub-0021_ses-01_task-social_acq-mb8_run-02_events.tsv',
        'sub-0021/ses-01/func/sub-0021_ses-01_task-social_acq-mb8_run-03_events.tsv',
        'sub-0021/ses-01/func/sub-0021_ses-01_task-social_acq-mb8_run-04_events.tsv']
        for typo_fname in typo_flist:
            c3_handle_typo_cases(f"{typo_fname}", 
                                corrected_subject_id=21, 
                                dest_fname=f"{typo_fname}",update_session_id=True)

        typo_flist = ['sub-0019/ses-04/func/sub-0019_ses-19_task-fractional_acq-mb8_run-01_events.tsv',
        'sub-0019/ses-04/func/sub-0019_ses-19_task-fractional_acq-mb8_run-02_events.tsv']
        for typo_fname in typo_flist:
            c3_handle_typo_cases(f"{typo_fname}", 
                                corrected_subject_id=19, 
                                dest_fname="sub-0019/ses-04/func/sub-0019_ses-04_task-fractional_acq-mb8_run-02_events.tsv",update_session_id=True)


