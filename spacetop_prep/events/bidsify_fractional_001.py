import pandas as pd
from os.path import join
# load csv file
file_dir = '/Users/h/Documents/projects_local/1076_spacetop'
flist = [
    'sub-0001/ses-04/func/sub-0001_ses-04_task-fractional_acq-mb8_run-01_events.tsv', 
    'sub-0001/ses-04/func/sub-0001_ses-04_task-fractional_acq-mb8_run-02_events.tsv'
    ]
for fname in flist:
    df = pd.read_csv(join(file_dir, fname), sep='\t')
    newdf = df.sort_values(by=['onset'])
    newdf.to_csv(join(file_dir, fname), sep='\t')