#!/usr/bin/env python3
"""
after downloading redcap data, convert it into table for Inclusion Enrollment Report
# multiindex
# grab rows that have "Consent" in it. "
# TODO: insert columns
# calculate totals
"""

import os, sys, glob
import itertools
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development" 

# %% load data from RedCap ___________________________________________________________________________
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[0]
csv_fname = os.path.join(main_dir, 'redcap', 'IndividualizedSpatia_DATA_LABELS_2022-03-22_1638.csv')
df = pd.read_csv(csv_fname)

# create empty dataframe ___________________________________________________________________________
eth = ['Not Hispanic or Latino', 'Hispanic or Latino', 'Unknown or Prefer Not to Answer']
gen = ['Female', 'Male', 'Other']
race = ['American Indian/Alaska Native', 'Asian',
'Black or African American','More than One Race','Native Hawaiian or Other Pacific Islander',
'Unknown or Prefer Not to Answer','White' ]
tuples = list(itertools.product(eth, gen))
columns = pd.MultiIndex.from_tuples(tuples, names=["Ethnicity", "Sex:"])
empty_df = pd.DataFrame(np.zeros((7,9)), index = race,columns =columns  )
empty_df.index.name = 'Race'

# select subset of IDs from Redcap ________________________________________________________________
sub = df[df['Record ID'].str.contains('sub-')]
sub = sub[~sub['Record ID'].str.contains('old')]
sub_i = sub.set_index('Record ID').copy()
# identify subjects that consented, then check their screening info for race, sex, ethnicity ______
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
df_final = pivot_sort.append([new_row])

# save file _______________________________________________________________________________________
date_str = datetime.date.today().isoformat()
df_final.to_csv(f'./ier-table_include-spacetop_{date_str}.csv')
df_ier.index.to_series().to_csv(f'./ier-subjects_include-spacetop_{date_str}.csv', index = False)

