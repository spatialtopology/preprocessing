"""Related to issue https://github.com/spatialtopology/spacetop-prep/issues/110
We will remove events.tsv rows that are longer than the collected BOLD TR slices. 

These cases will occur, when a scan was aborted earlier than expected,
but when the stimulus PC continued to collect data while scan operator was troubleshooting on the scanner end.

Examples: participant squeeze emergency ball towards the end of the run, reporting equipment failure. 
Scan was aborted 41 seconds earlier than expected. Stimulu PC behavioral data was collected entirely

This code will remove the extra rows from the events.tsv file , which will match the legnth of the bOLD data
and resolve the bids-validator errors of "SUSPICIOUSLY_LONG_EVENT_DESIGN"
"""

import os
import json
import numpy as np
import pandas as pd

# file list is identified via Yarik Halchenko. 
# check out description in issue #110 in spatialtopology spacetop-prep
flist = ['sub-0013/ses-04/func/sub-0013_ses-04_task-fractional_acq-mb8_run-01_bold.nii.gz',
         'sub-0017/ses-04/func/sub-0017_ses-04_task-social_acq-mb8_run-04_bold.nii.gz',
         'sub-0035/ses-01/func/sub-0035_ses-01_task-alignvideo_acq-mb8_run-02_bold.nii.gz',
         'sub-0055/ses-02/func/sub-0055_ses-02_task-narratives_acq-mb8_run-04_bold.nii.gz',
         'sub-0061/ses-01/func/sub-0061_ses-01_task-alignvideo_acq-mb8_run-03_bold.nii.gz',
         'sub-0069/ses-02/func/sub-0069_ses-02_task-narratives_acq-mb8_run-03_bold.nii.gz',
         'sub-0084/ses-03/func/sub-0084_ses-03_task-alignvideo_acq-mb8_run-01_bold.nii.gz']

# get BOLD data TR (dcmmeta_shape[-1])
for fpath in flist:
    # Get the base filename and construct paths for the .json and events.tsv files
    basename = os.path.basename(fpath)
    json_path = fpath.replace('_bold.nii.gz', '_bold.json')
    events_path = fpath.replace('_bold.nii.gz', '_events.tsv')

    # Load JSON metadata to retrieve BOLD TR duration
    with open(json_path, 'r') as json_file:
        metadata = json.load(json_file)
        number_of_dynamics = metadata.get('dcmmeta_shape', [])[3]  # Assuming TR duration is the 4th value
        tr = metadata['RepetitionTime']

    # Load the events.tsv file
    events_df = pd.read_csv(events_path, sep='\t', dtype=str)


    # remove rows that exceed BOLD data TR
    max_scan_time = tr * number_of_dynamics

    # filtered_events_df = events_df[events_df['onset'] + events_df['duration'] <= max_scan_time]
    onsets = pd.to_numeric(events_df['onset'], errors='coerce')
    invalid_rows_df = events_df.loc[(onsets > max_scan_time) & (~onsets.isna())]
    
    if not len(invalid_rows_df):
        print(f"No invalid rows detected in {events_path}")
        continue
    first_invalid_row = invalid_rows_df.head(1)
    first_invalid_index = first_invalid_row.index.to_list()[0]

    filtered_events_df = events_df.iloc[:first_invalid_index]
    rows_removed = len(events_df) - len(filtered_events_df)
    print(f"The events.tsv for {basename} has last event {(events_df['onset'].iloc[-1])} and is {len(events_df)} long.\n The expected last event should be <= {max_scan_time}. We'll shave off {rows_removed} rows to match expected length")
    # save file
    filtered_events_df.to_csv(events_path, sep='\t', index=False, na_rep='n/a')
