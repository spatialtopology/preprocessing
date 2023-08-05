# %%
import os, re, glob
import argparse
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from pathlib import Path
from nilearn.datasets import fetch_language_localizer_demo_dataset
from nilearn.glm.first_level import first_level_from_bids
from nilearn.glm.first_level import FirstLevelModel
from nilearn import image, plotting
import itertools
from os.path import join

# ----------------------------------------------------------------------
#                            load GUID data
# ----------------------------------------------------------------------
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[0] #
save_dir = join(main_dir, 'DEP_nda_beh')
guid_df = pd.read_csv(join(main_dir, 'nda', 'ndar_subject.csv'))
sub_list = guid_df.src_subject_id.tolist()

# ----------------------------------------------------------------------
#                          load behavioral data
# ----------------------------------------------------------------------
beh_flist = []
for sub in sub_list:
    sub_flist = glob.glob(f'/Users/h/Documents/projects_local/cue_expectancy/data/fmri/fmri01_onset/onset02_SPM/{sub}/ses-*/*_events.tsv', recursive=True)
    beh_flist.append(sub_flist)
flattened_list = list(itertools.chain.from_iterable(beh_flist))

for beh_fname in flattened_list:
    beh_df = pd.read_csv(beh_fname,  sep='\t')
    beh_df = beh_df.drop(['cue_con', 'stim_lin', 'stim_quad', 'pmod_expectangle_demean', 'pmod_outcomeangle_demean'], axis=1)

    # # ====== NOTE: insert new BIDScolumns
    # 'src_subject_id', 'session_id', 'run_num', 'run_type', 'trial_num'
    pattern = r'sub-(\d+)_ses-(\d+)_task-\w+_run-(\d+)_runtype-(\w+)_events\.tsv'
    match = re.match(pattern, os.path.basename(beh_fname))
    if match:
        sub_id = f"sub-{match.group(1)}" 
        session_id = f"ses-{match.group(2)}"  
        run_num = f"run-{match.group(3)}" 
        run_type = match.group(4)
        bidsdf = pd.DataFrame()
        # Create a DataFrame with the extracted substrings
        data = {'src_subject_id': [sub_id],
                'session_id': [session_id],
                'run_num': [run_num],
                'run_type':[run_type]}
        bidsdf = pd.DataFrame(data)
    else:
        print("No match found.")

    # ====== NOTE: behavioral dataframe with BIDS appended
    beh_bids_df = pd.concat([pd.concat([bidsdf] * len(beh_df), ignore_index=True), beh_df], axis = 1)
    beh_bids_df = beh_bids_df.drop('src_subject_id', axis=1)
    # sub_id = beh_fname[beh_fname.find('sub-'):beh_fname.find('/', beh_fname.find('sub-'))]

    # ====== NOTE: grab corresonding subject's GUID data and merge
    sub_guid = guid_df.loc[(guid_df['src_subject_id'] == sub_id) & (guid_df['session_id'] == session_id), :]
    sub_guid = sub_guid.drop(['index','Unnamed: 0', 'birth_Y_m_d', 'session_id'], axis=1)
    repeated_df = pd.concat([sub_guid] * len(beh_bids_df), ignore_index=True)# drop columns
    # Index(['Unnamed: 0', 'subjectkey', 'src_subject_id', 'birth_Y_m_d', 'sex',
    #        'race', 'ethnic_group', 'phenotype', 'phenotype_description',
    #        'twins_study', 'sibling_study', 'family_study', 'interview_date',
    #        'interview_age'],
    merge_df = pd.concat([repeated_df, beh_bids_df], axis=1) #, ignore_index=True)
    sub_save_dir = join(save_dir, sub_id)
    Path(sub_save_dir).mkdir(parents=True, exist_ok=True)
    merge_df.to_csv(join(sub_save_dir, os.path.splitext(os.path.basename(beh_fname))[0] + '.csv'), index=False)

# %% Definitions file
dtypes_df = pd.DataFrame(merge_df.dtypes.reset_index())
dtypes_df.columns = ['ElementName', 'DataType' ] #, 'Size', 'ElementDescription', 'ValueRange', 'Notes', 'Aliases']
dtypes_df.to_csv(join(save_dir, 'placebo_cue_definitions.csv'), index=False)

# dtypes_df = pd.DataFrame(columns=['ElementName', 'DataType', 'Size', 'ElementDescription', 'ValueRange', 'Notes', 'Aliases'])
# # pd.DataFrame(merge_df.dtypes.reset_index())
# dtypes_df.loc[:, 'ElementName':'DataType'] = pd.DataFrame(merge_df.dtypes.reset_index()).values

