# %%
import os
from itertools import cycle
from os.path import join
from pathlib import Path

import numpy as np
import pandas as pd

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Melanie Kos"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

# %% 01 load and merge dataframes with the following: _________________________________________________
#   1) study id
#   2) GUID
#   3) Race ethnicity information
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[0]
# load spacetop_GUID_BIDS.csv: this is the one that was submitted to NDA GUID. It houses the subject ids.
study_id = pd.read_csv(os.path.join(main_dir, 'nda', 'PRIVATE_spacetop_GUID_BIDS.csv'))
# load GUID csv: generated from NDA
guid = pd.read_csv(os.path.join(main_dir, 'nda', 'spacetop_GUID--results-20230517T194253830Z.csv'))
# load the spacetop data from REDcap. This one houses the race and ethnicity information.
race_eth = pd.read_csv(os.path.join(main_dir, 'nda', 'PRIVATE_spacetop_raceth.csv'))

merged_df = pd.merge(guid, study_id, left_on='RECORD_ID', right_on='ID')
df = pd.merge(merged_df, race_eth, on = 'Record ID')
# %% 02 Add generic NDA information _________________________________________________
df["phenotype"] = "Not Applicable"
df["phenotype_description"] = "Not Applicable"
df["twins_study"] = "No"
df["sibling_study"] = "No"
df["family_study"] = "No"
df_rename = df.rename(columns={'Race:': 'race',
                  'Ethnicity:': 'ethnic_group',
                  'SEX': 'sex',
                  'Date of birth:': 'birth_Y_m_d',
                  'Record ID': 'src_subject_id',
                  'GUID':'subjectkey'})
df_subset = df_rename[['subjectkey', 'src_subject_id', 'birth_Y_m_d',
                'sex', 'race', 'ethnic_group',
                'phenotype', 'phenotype_description',
                'twins_study', 'sibling_study', 'family_study']]

# %% 03 layer in interview date information _________________________________________________
interview = pd.read_csv(join(main_dir, 'nda', 'PRIVATE_spacetop_interviewdate.csv'))

df_subsetlong = df_subset.loc[df_subset.index.repeat(4)] # 1) repeat each row 4 times
df_subsetlong['session_id']  = np.tile(['ses-01', 'ses-02', 'ses-03', 'ses-04'], len(df_subset)) # 2) create session_id column and repeat session sequence

# a) convert dataframe wide-to-long -> merge outputs based on reset index
# also add src_subject_id, repeating it 4 times for the 4 sessions
ses_list = ['ses-01_Date', 'ses-02_Date', 'ses-03_Date', 'ses-04_Date']
age_list = ['Age_ses-01', 'Age_ses-02', 'Age_ses-03', 'Age_ses-04']
interview_ses = pd.melt(interview, value_vars=ses_list,value_name='interview_date', ignore_index=False)
interview_age = pd.melt(interview, value_vars=age_list,value_name='interview_age', ignore_index=False)
interview_final = pd.merge(interview_ses.reset_index(), interview_age.reset_index(), left_index=True, right_index=True) # based on index
interview_final['src_subject_id'] = np.tile(interview['Record ID'], 4)

# b) match on src_subject_id and session info , add interview datte
guiddf = df_subsetlong.reset_index()
for index, row in guiddf.iterrows():
    subset = interview_final[(interview_final["src_subject_id"] == row["src_subject_id"]) & (interview_final["variable_x"].str.contains(row["session_id"]))]
    if not subset.empty:
        guiddf.at[index, "interview_date"] = subset["interview_date"].iloc[0]
        guiddf.at[index, "interview_age"] = subset["interview_age"].iloc[0]

# c) save dataframe
guiddf.to_csv(os.path.join(main_dir, 'nda', 'ndar_subject.csv'))
