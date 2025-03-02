import pandas as pd
# load csv file
flist = [
    'sub-0001/ses-04/func/sub-0001_ses-04_task-fractional_acq-mb8_run-01_events.tsv', 
    'sub-0001/ses-04/func/sub-0001_ses-04_task-fractional_acq-mb8_run-02_events.tsv'
    ]
for fname in flist:
    df = pd.read_csv(fname, sep='\t')
    newdf = df.sort_values(by=['onset'])
    newdf.to_csv(fname)