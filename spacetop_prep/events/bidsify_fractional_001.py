import pandas as pd
from os.path import join
from pathlib import Path
import os, re
# load csv file


def get_task_name(bids_string, metadata_df):
    '''
    Retrieve the task name based on subject ID and run ID (run-01 or run-02).
    
    Parameters:
        subject_id (str): The subject ID in the form 'sub-0006'.
        run_id (str): The run ID, either 'run-01' or 'run-02'.
    
    Returns:
        str: The task name or an error message if the input is invalid.
    '''
    # Convert subject_id to integer by removing the 'sub-' prefix
    fname = Path(bids_string).stem
    sub = extract_bids(fname, 'sub')
    run = re.search(r'run-\d+', fname).group(0)
    # run = extract_bids(fname, 'run')
    subject_number = int(sub.replace('sub-', ''))
    
    # Map run_id to task1 or task2
    run_map = {
        'run-01': 'task1',
        'run-02': 'task2'
    }
    
    if run not in run_map:
        return 'Error: run_id should be either \'run-01\' or \'run-02\''
    
    # Find the row with the matching subject ID
    subject_row = metadata_df[metadata_df['subject'] == subject_number]
    
    if subject_row.empty:
        return f'Error: No data found for subject ID {sub}'
    
    # Retrieve the task name for the specified run ID
    task_column = run_map[run]
    task_name = subject_row[task_column].values[0]
    return task_name


file_dir = '/Users/h/Documents/projects_local/1076_spacetop'
flist = [
    'sub-0001/ses-04/func/sub-0001_ses-04_task-fractional_acq-mb8_run-01_events.tsv', 
    'sub-0001/ses-04/func/sub-0001_ses-04_task-fractional_acq-mb8_run-02_events.tsv'
    ]
for fname in flist:
    if Path(join(file_dir, fname)).exists():
        df = pd.read_csv(join(file_dir, fname), sep='\t')
        newdf = df.sort_values(by=['onset'])
        newdf_na = newdf.fillna('n/a')
        newdf_na.to_csv(join(file_dir, fname), sep='\t', index=False)


# tomspunt
# df = pd.read_csv(join(file_dir, fname), sep='\t')
spunt_fpath = '/Users/h/Documents/projects_local/d_beh/sub-0001/task-fractional/sub-0001_ses-04_task-fractional_run-02-tomspunt_beh.csv'
metadata_df = pd.read_csv(join('/Users/h/Documents/projects_local/1076_spacetop/code/spacetop-prep/spacetop_prep/events', 'spacetop_task-fractional_run-metadata.csv'))

events_spunt = pd.DataFrame()

spunt_fname = os.path.basename(spunt_fpath)
sub_bids = re.search(r'sub-\d+', spunt_fname).group(0)
ses_bids = re.search(r'ses-\d+', spunt_fname).group(0)
run_bids = re.search(r'run-\d+', spunt_fname).group(0)
bids_name= f'{sub_bids}_{ses_bids}_{run_bids}'
task_name = get_task_name(bids_name, metadata_df)
# task_name = re.search(r'run-\d+-(\w+)_beh', spunt_fname).group(1)

print(f'{sub_bids} {ses_bids} {run_bids} {task_name}')
beh_savedir = join('/Users/h/Documents/projects_local/1076_spacetop', sub_bids, ses_bids, 'func')

df_spunt = pd.read_csv(spunt_fpath)
df_spunt['trial_index'] = df_spunt.index + 1

events_spunt = pd.DataFrame(columns=['onset', 'duration', 'subtask_type', 'question', 'event_type','participant_response', 'normative_response', 'response_accuracy', 'stim_file']) 
blockquestion = pd.DataFrame(columns=['onset', 'duration', 'subtask_type', 'question', 'event_type','participant_response', 'normative_response', 'response_accuracy', 'stim_file']) 

events_spunt['onset'] = df_spunt['RAW_e2_image_onset'] - df_spunt['param_trigger_onset']
events_spunt['duration'] = df_spunt['RAW_e3_response_onset'] - df_spunt['RAW_e2_image_onset'] 
events_spunt['subtask_type'] = 'tomspunt'
events_spunt['question'] = df_spunt['param_ques_type_string']
df_spunt['event_type'] = df_spunt['param_cond_type_string'].str.replace('^(c[1234])_', '', regex=True).str.replace(r'([a-z])([A-Z])', r'\1_\2').str.lower()
events_spunt['participant_response'] = df_spunt['event03_response_keyname'].replace({'left': 'yes', 'right':'no'})
events_spunt['normative_response'] = df_spunt['param_normative_response'].replace({1:'yes', 2:'no'})
events_spunt['event_type'] = df_spunt['event_type'].str[:3] + '_' + df_spunt['event_type'].str[3:]
events_spunt['stim_file'] = 'task-tomspunt/' + df_spunt['param_image_filename']
df_spunt['reponse_subject'] = df_spunt['event03_response_key'].replace(3, 2)
events_spunt['response_accuracy'] = (events_spunt['participant_response'] == events_spunt['normative_response']).astype(int).replace({1: 'correct', 0: 'incorrect'})
events_spunt['trial_index'] = df_spunt['trial_index']

block_key = df_spunt.drop_duplicates(subset=['event01_blockquestion_onset'])
blockquestion['onset'] = block_key['event01_blockquestion_onset']
blockquestion['duration'] = block_key['event01_blockquestion_dur']
blockquestion['subtask_type'] = 'tomspunt'
blockquestion['question'] = block_key['param_ques_type_string']
blockquestion['event_type'] = 'block_question_presentation'
blockquestion['participant_response'] = 'n/a'
blockquestion['normative_response'] = 'n/a'
blockquestion['stim_file'] = 'n/a'
blockquestion['response_accuracy'] = 'n/a'
blockquestion['trial_index'] = block_key['trial_index']
# block_unique = blockquestion.drop_duplicates()
print(df_spunt[['trial_index']].head())
print(blockquestion[['trial_index']].head())

events_spunt = pd.concat([events_spunt, blockquestion], ignore_index=True)
precision_dic = {'onset': 3, 'duration': 3}
events_spunt = events_spunt.round(precision_dic)
events_spunt['onset'] = pd.to_numeric(events_spunt['onset'], errors='coerce')

# events_spunt = events_spunt.sort_values(by='onset')
events_spunt = events_spunt.sort_values(by=['onset', 'trial_index'])
events_spunt = events_spunt.fillna('n/a')
events_spunt = events_spunt.reset_index(drop=True)

Path(beh_savedir).mkdir( parents=True, exist_ok=True )
save_fname = f'{sub_bids}_{ses_bids}_task-fractional_acq-mb8_{run_bids}_events.tsv'
events_spunt.to_csv(join(beh_savedir, save_fname), sep='\t', index=False)

