"""
Harmonize the REDcap downloaded file for GUID submission
ID
FIRSTNAME
MIDDLENAME
LASTNAME
MOB
DOB
YOB
COB
SEX
SUBJECTHASMIDDLENAME
"""
import os
from pathlib import Path

# %%
import pandas as pd

current_dir = os.getcwd()
main_dir = Path(current_dir).parents[0]

df = pd.read_csv(os.path.join(main_dir, 'redcap/IndividualizedSpatia-NDA_DATA_LABELS_2023-05-17_1435.csv'))
# %%
# remap SEX
gender_mapping = {'Male': 'M', 'Female': 'F'}
df['SEX'] = df['Sex at birth:'].replace(gender_mapping)

df['Birth'] = pd.to_datetime(df['Date of birth:'], format='%Y-%m-%d')
df['MOB'] = df['Birth'].dt.month
df['DOB'] = df['Birth'].dt.day
df['YOB'] = df['Birth'].dt.year
# remove the nans from middlename
df['MIDDLENAME'] = df["Middle name (if you do not have a middle name, type 'N/A'): "].fillna('')
# create a column if middle name is not empty
df['Is_Empty'] = df['MIDDLENAME'].str.strip().str.len() > 0
df['SUBJECTHASMIDDLENAME'] = df['Is_Empty'].map({True: 'YES', False: 'NO'})
# df['City/municipality of birth:'].str.
df['COB'] = df['City/municipality of birth:'].str.split(',', n=1, expand=True)[0]
# change column names
df = df.rename(columns={'First Name:': 'FIRSTNAME',
                  'Last Name:': 'LASTNAME'})
df['ID'] = df['Record ID'] #[index + 1 for index in df.index]
# reorder columns
column_list = ['ID', 'FIRSTNAME', 'MIDDLENAME', 'LASTNAME', 'MOB', 'DOB', 'YOB', 'COB', 'SEX', 'SUBJECTHASMIDDLENAME']
df_final = df[column_list]
df_final.to_csv(os.path.join(main_dir, 'redcap', 'spacetop_GUID.csv'), index=False)
column_list.append('Record ID')
df_BIDS = df[column_list]
df_BIDS.to_csv(os.path.join(main_dir, 'redcap', 'spacetop_GUID_BIDS.csv'), index=False)



# %%
