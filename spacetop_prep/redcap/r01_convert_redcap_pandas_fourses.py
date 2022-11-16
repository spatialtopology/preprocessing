#!/usr/bin/env python3
"""
The purpose of this script is to convert redcap data (ethnicity, gender, race)
into a table for Inclusion Enrollment Report

Parameters
------------
    csv_fname: str
        the REDcap downloaded file, which contains ethnicity, gender, race information
Return
------------
    df_tally: pandas dataframe
        a table with tally of ethnicity, gender, race information. Saved as csv file
    df_ier.index: list
        a list of participants that were included in the tally. Saved as csv file
"""
# %%
import os, sys, glob
import itertools
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

__author__ = "Heejung Jung"
__copyright__ = "Canlab Utils"
__credits__ = [""] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__github__ = "jungheejung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development" 


# %% load data from RedCap ___________________________________________________________________________
# TODO: Dear user, change csv_fname to your filename
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[0]
csv_fname = os.path.join(main_dir, 'redcap', 'IndividualizedSpatia_DATA_LABELS_2022-07-11_1618.csv') # NOTE: CHANGE THIS TO YOUR OWN FILENAME
df = pd.read_csv(csv_fname)

# create empty dataframe with ethnicity, gender, and race  ___________________________________________________________________________
eth = ['Not Hispanic or Latino', 'Hispanic or Latino', 'Unknown or Prefer Not to Answer']
gen = ['Female', 'Male', 'Other']
race = ['American Indian/Alaska Native', 'Asian',
'Native Hawaiian or Other Pacific Islander',
'Black or African American','White','More than One Race',
'Unknown or Prefer Not to Answer' ]
tuples = list(itertools.product(eth, gen))
columns = pd.MultiIndex.from_tuples(tuples, names=["Ethnicity", "Sex:"])
empty_df = pd.DataFrame(np.zeros((7,9)), index = race,columns =columns  )
empty_df.index.name = 'Race'
# %%
# select subset of IDs from Redcap ________________________________________________________________
# sub = df[df['Record ID'].str.contains('sub-')]
# sub = sub[~sub['Record ID'].str.contains('old')]
# NOTE: User, if you have any id's that you'd like to exclude, feed in a list to 'dup'
dup = ['old-sub-0055','old-sub-0103','old-sub-0118','old-sub-0128','old-sub-0130',
'old-sub-0131','old_sub-0020','C-NA-36 (1)','C-NA-88 (2)','N-NA-260 (2)',
'IE-9 (2)','IE-10 (2)','IE-23 (2)','IE-23 (3)','IE-43 (2)','IE-43 (3)',
'IE-63 (2)','C-NA-36 (1)','IE-7','IE-8', 'IE-19', 'N-NA-279', 'N-NR-217']
withdraw = [
'sub-0030',
'sub-0067',
'sub-0113',
'sub-0114',
'sub-0117',
'sub-0012',
'sub-0015',
'sub-0022',
'sub-0027',
'sub-0028',
'sub-0042',
'sub-0045',
'sub-0047',
'sub-0048',
'sub-0049',
'sub-0054',
'sub-0063',
'sub-0068',
'sub-0071',
'sub-0072',
'sub-0082',
'sub-0085',
'sub-0096',
'sub-0097',
'sub-0108',
'sub-0110',
'sub-0118',
'sub-0119',
'sub-0120',
'sub-0121',
'sub-0123',
'sub-0125']
#sub = df[~df['Record ID'].str.contains('|'.join(dup))]
sub = df[df['Record ID'].str.contains('sub-0')]
filter_sub = sub[sub['Record ID'].str.contains('|'.join(dup))==False]
#df = df[df['Record ID'].str.contains('|'.join(dup))==False]
sub_i = filter_sub.set_index('Record ID').copy()
# identify subjects that consented, then check their screening info for race, sex, ethnicity ______
# %%
sub_consent = sub_i[sub_i['Event Name'].str.contains('Consent')]
sub_screen = sub_i[sub_i['Event Name'].str.contains('Screening')]
df_consent = sub_screen.loc[list(sub_consent.index) ]
df_ier = df_consent[['Sex:', 'Race', 'Ethnicity']]

# pivot and calculate frequency of race/ethnicity/sex _____________________________________________
pivot = df_ier.pivot_table(index='Race',
               columns=['Ethnicity', 'Sex:'],
               aggfunc=len,
               fill_value=0)

df_concat = pd.concat([empty_df, pivot],sort = False)
df_concat = df_concat.groupby(level = 0).sum()
new_cols = df_concat.columns.reindex(eth, level=0)
pivot_sort = df_concat.reindex(index = race, columns = new_cols[0])

pivot_sort['Total']=pivot_sort.iloc[:,:].sum(axis=1)
new_row = pivot_sort.iloc[:,:].sum(axis = 0) 
new_row.name = 'Total'
df_tally = pivot_sort.append([new_row])

# save file _______________________________________________________________________________________
date_str = datetime.date.today().isoformat()
df_tally.to_csv(f'./ier-table_include-foursessiononly_{date_str}.csv')
df_ier.index.to_series().to_csv(f'./ier-subjects_include-foursessiononly_{date_str}.csv', index = False)

# %%
