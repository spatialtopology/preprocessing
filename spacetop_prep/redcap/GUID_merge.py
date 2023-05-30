# %%
import os
from pathlib import Path

import numpy as np
import pandas as pd

current_dir = os.getcwd()
main_dir = Path(current_dir).parents[0]
# load GUID csv: generated from NDA
guid = pd.read_csv(os.path.join(main_dir, 'redcap/spacetop_GUID--results-20230517T194253830Z.csv'))
# load spacetop_GUID_BIDS.csv: this is the one that was submitted to NDA GUID. It houses the subject ids.
spacetop_data = pd.read_csv(os.path.join(main_dir, 'redcap/spacetop_GUID_BIDS.csv'))
# load tthe spacetop data from REDcap. This one houses the race and ethnicity information.
spacetop = pd.read_csv(os.path.join(main_dir, 'redcap/IndividualizedSpatia-NDA_DATA_LABELS_2023-05-17_1435.csv'))


merged_df = pd.merge(guid, spacetop_data, left_on='RECORD_ID', right_on='ID')
df = pd.merge(merged_df, spacetop, on = 'Record ID')
# %%

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

df_subset[[ 'interview_date', 'interview_age']] = np.nan
# %%
df_subset.to_csv(os.path.join(main_dir, 'redcap', 'ndar_subject.csv'))
# %%
