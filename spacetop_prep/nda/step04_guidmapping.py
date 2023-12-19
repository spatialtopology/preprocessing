# %%
import os
from pathlib import Path
from os.path import join
import pandas as pd

# Read the CSV file
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[0] #
# save_dir = join(main_dir, 'DEP_nda_beh')
guid_df = pd.read_csv(join(main_dir, 'nda', 'ndar_subject.csv'))
# %%
# Format the columns into a text file
formatted_data = guid_df['src_subject_id'].str.extract(r'sub-(\d+)').squeeze() + ' - ' + guid_df['subjectkey'].astype(str)

# Save the formatted data to a text file
formatted_data.to_csv(join(main_dir, 'nda', 'GUIDMAPPING.txt'), index=False, header=False)
