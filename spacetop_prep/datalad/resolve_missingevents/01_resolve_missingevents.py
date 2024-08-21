
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
import os, glob, sys
import subprocess
import pandas as pd
from itertools import zip_longest
from pathlib import Path
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
    print(sub,ses,task,run)
    if task == "task-alignvideo":
        task = "task-alignvideos"

    base_path = f"/home/spacetop/repos/{repo2task_dict[task]}/data/{sub}/{ses}/beh"
    # Adjust paths and patterns based on task type
    if task == "task-shortvideos":
        base_path = f"/home/spacetop/repos/{repo2task_dict[task]}/data/{sub}/ses-03/beh"
    elif task == "task-faces":
        base_path = f"/home/spacetop/repos/{repo2task_dict[task]}/data/{sub}/beh/ses-02"
    elif task == "task-narratives":
        base_path = f"/home/spacetop/repos/{repo2task_dict[task]}/data/{sub}/beh/"
    
    file_pattern = f"{sub}*{ses}*{task}*{run}*TEMP*beh.csv" if task in ["task-alginvideo", "task-social"] else f"{sub}*{task}*TEMP*beh.csv"
    os.chdir(base_path)
    for file in glob.glob(file_pattern):
        print(file)
        
        if task == "task-social" or task=="task-alignvideos":
            destination = f"/home/spacetop/repos/data/{sub}/{task}/{ses}/{sub}_{ses}_{task}_{run}_beh_TEMP.csv"
        else:
            destination = f"/home/spacetop/repos/data/{sub}/{task}/{sub}_{ses}_{task}_{run}_beh_TEMP.csv"

        subprocess.run(["cp", file, destination])
        print(destination)
        os.chdir("/home/spacetop/repos/data")
        subprocess.run(["git", "add", destination])
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
        subprocess.run(["git", "mv", typo_fname, dest_fname])
        typo_fname = dest_fname
    
    # Load the file into a DataFrame
    typodf = pd.read_csv(dest_fname)
    
    # Update the 'src_subject_id' column if corrected_subject_id is provided
    if corrected_subject_id:
        typodf['src_subject_id'] = corrected_subject_id
    
    # Update the 'session_id' column if required
    if update_session_id and 'session_id' in typodf.columns:
        # Extract the session ID from the filename or corrected subject ID
        session_id = os.path.basename(dest_fname).split('ses-')[1].split('_')[0] if dest_fname else corrected_subject_id.split('-')[-1]
        typodf['session_id'] = int(session_id)
    
    # Save the updated DataFrame back to the file
    print(typodf.head(5))
    typodf.to_csv(dest_fname, index=False)
    
    # Add the file to Git and commit the changes
    os.chdir("/home/spacetop/repos/data")
    subprocess.run(["git", "add", os.path.expanduser(dest_fname)])
    subprocess.run(["git", "commit", "-m", "BUG: resolve typo and update BIDS fields"])

sys.stdout = open('output.log', 'w')


# Load the TSV file into a DataFrame
df = pd.read_csv('./missing_events_manual_inspection.tsv', sep='\t')

# Define a dictionary for repo2task mapping
repo2task_dict = {
    "task-alignvideos": "alignvideos",
    "task-fractional": "fractional",
    "task-social": "social_influence",
    "task-faces": "faces",
    "task-narratives": "narratives",
    "task-shortvideos": "shortvideos"
}

for _, row in df.iterrows():
    sub = extract_bids(os.path.basename(row['BIDS_string']), 'sub')
    ses = extract_bids(os.path.basename(row['BIDS_string']), 'ses')
    run = extract_bids(os.path.basename(row['BIDS_string']), 'run')
    task = extract_bids(os.path.basename(row['BIDS_string']), 'task')

    if row['case'] == 'C1':
        # if case 1, copy over TEMP files from git repo
        c1_process_temp_files(sub, ses, task, run, repo2task_dict)
    
    elif row['case'] == 'C3':
        # c3_handle_typo_cases('/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0156_ses-04_task-alignvideos_run-01_beh.csv', 
                            #  corrected_subject_id=16, 
                            #  dest_fname="/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0016_ses-04_task-alignvideos_run-01_beh.csv",update_session_id=True)
        typo_flist = ['/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0156_ses-04_task-alignvideos_run-01_beh.csv',
                      '/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0156_ses-04_task-alignvideos_run-01_TEMP_beh.csv',
                      '/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0156_ses-04_task-alignvideos_run-02_beh.csv',
                      '/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0156_ses-04_task-alignvideos_run-02_TEMP_beh.csv']
        fix_flist = ['/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0016_ses-04_task-alignvideos_run-01_beh.csv',
                      '/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0016_ses-04_task-alignvideos_run-01_TEMP_beh.csv',
                      '/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0016_ses-04_task-alignvideos_run-02_beh.csv',
                      '/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04/sub-0016_ses-04_task-alignvideos_run-02_TEMP_beh.csv']
        for typo_fname, fix_fname in zip_longest(typo_flist, fix_flist):
            c3_handle_typo_cases(typo_fname, 
                                corrected_subject_id=16, 
                                dest_fname=fix_fname,update_session_id=True)

        directory = Path('/home/spacetop/repos/data/sub-0016/task-alignvideos/ses-04')
        for old_filename in directory.glob('sub-0156_ses-04*.mat'):
            new_filename = old_filename.with_name(old_filename.name.replace('sub-0156', 'sub-0016'))     # Create the new filename by replacing part of the string
            old_filename.rename(new_filename)

        # sub-0098 -> sub-0021
        typo_flist = ['/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0098_ses-01_task-social_run-01-pain_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0098_ses-01_task-social_run-02-cognitive_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0098_ses-01_task-social_run-03-vicarious_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0098_ses-01_task-social_run-04-cognitive_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0098_ses-01_task-social_run-05-pain_beh.csv']
        fix_flist = ['/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0021_ses-01_task-social_run-01-pain_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0021_ses-01_task-social_run-02-cognitive_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0021_ses-01_task-social_run-03-vicarious_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0021_ses-01_task-social_run-04-cognitive_beh.csv',
        '/home/spacetop/repos/data/sub-0021/task-social/ses-01/sub-0021_ses-01_task-social_run-05-pain_beh.csv']

        for typo_fname, fix_fname in zip_longest(typo_flist, fix_flist):
            c3_handle_typo_cases(typo_fname, 
                                corrected_subject_id=21, 
                                dest_fname=fix_fname,update_session_id=True)
            
        directory = Path('/home/spacetop/repos/data/sub-0021/task-social/ses-01')
        for old_filename in directory.glob('sub-0098*.mat'):
            new_filename = old_filename.with_name(old_filename.name.replace('sub-0098', 'sub-0021'))     # Create the new filename by replacing part of the string
            old_filename.rename(new_filename)


        # ses-19 -> ses-04
        typo_flist = ['/home/spacetop/repos/data/sub-0019/task-fractional/sub-0019_ses-19_task-fractional_run-01-tomspunt_beh.csv',
        '/home/spacetop/repos/data/sub-0019/task-fractional/sub-0019_ses-19_task-fractional_run-02-posner_beh.csv']
        fix_flist = ['/home/spacetop/repos/data/sub-0019/task-fractional/sub-0019_ses-04_task-fractional_run-01-tomspunt_beh.csv',
        '/home/spacetop/repos/data/sub-0019/task-fractional/sub-0019_ses-04_task-fractional_run-02-posner_beh.csv']

        for typo_fname, fix_fname in zip_longest(typo_flist, fix_flist):
            c3_handle_typo_cases(typo_fname, 
                                corrected_subject_id=19, 
                                dest_fname=fix_fname,update_session_id=True)
            
        directory = Path('/home/spacetop/repos/data/sub-0019/task-fractional/ses-04')
        for old_filename in directory.glob('sub-0019_ses-19*.mat'):
            new_filename = old_filename.with_name(old_filename.name.replace('ses-19', 'ses-04'))     # Create the new filename by replacing part of the string
            old_filename.rename(new_filename)

sys.stdout = sys.__stdout__
print("complete")
