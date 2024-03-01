# Generate events files for task-narratives

# This script reads raw behavior data files from d_beh for task-narratives, extracts time stamps and design information, and stores them in new *events.tsv files accompanying BOLD files.

# For more information, please see README.md and the associated paper (Jung et al., 2024)

import os
import glob
import pandas as pd
import numpy as np

# please change `behDataDir` to the top level of the `d_beh` directory
# >>>
behDataDir = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata/d_beh'
# please change `outputDir` to the top level of the BIDS directory
# >>>
outputDir = '/Users/h/Documents/projects_local/1076_spacetop'

# get a list of subjects with behavior data
folders = glob.glob(os.path.join(outputDir, 'sub-*'))
subList = [os.path.basename(x) for x in folders]
taskname = 'task-narratives'
session = 'ses-02'

for sub in subList:
    for run in ['01', '02', '03', '04']:
        
        dataFile = os.path.join(behDataDir, sub, taskname, f'{sub}_{session}_{taskname}_run-{run}_beh-preproc.csv')
        if not os.path.isfile(dataFile):
            print(f'No behavior data file for {sub}_run-{run}')
            continue

        oriData = pd.read_csv(dataFile)
        newData = pd.DataFrame(columns=["onset", "duration", "trial_type", 
                                "response_x", "response_y",
                                "situation", "context", "modality", "stim_file"])    # new events to store
        if run in ['01', '02']:
            modality = 'Audio'
        else:
            modality = 'Text'
        
        t_runStart = oriData.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

        for t in range(len(oriData)):    # each trial
            # Event 1. narrative presentation
            onset = oriData.loc[t, 'event02_administer_onset'] - t_runStart
            duration = oriData.loc[t, 'event03_feel_displayonset'] - oriData.loc[t, 'event02_administer_onset']
            trial_type = "narrative_presentation"
            situation = oriData.loc[t, 'situation']
            context = oriData.loc[t, 'context']
            stim_file = oriData.loc[t, 'param_stimulus_filename']
            stim_file = stim_file[:20] + '.mp3' if run in ['01', '02'] else stim_file[:20] + '.txt'
            stim_file = 'task-narratives/' + stim_file
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                            "situation": situation, "context": context, "modality": modality, "stim_file": stim_file}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)

            # Event 2. feeling rating
            onset = oriData.loc[t, 'event03_feel_displayonset'] - t_runStart
            duration = oriData.loc[t, 'RT_feeling'] if ~np.isnan(oriData.loc[t, 'RT_feeling']) else oriData.loc[t, 'RT_feeling_adj']
            trial_type = 'rating_feeling'
            response_x = oriData.loc[t, 'feeling_end_x']
            response_y = oriData.loc[t, 'feeling_end_y']
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                            "response_x": response_x, "response_y": response_y, \
                            "situation": situation, "context": context, "modality": modality}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)
            
            # Event 3. feeling mouse trajectory
            onset += oriData.loc[t, 'motion_onset_feeling']
            duration = oriData.loc[t, 'motion_dur_feeling']
            trial_type = 'feeling_mouse_trajectory'
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                            "response_x": response_x, "response_y": response_y, \
                            "situation": situation, "context": context, "modality": modality}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)

            # Event 4. expectation rating
            onset = oriData.loc[t, 'event04_expect_displayonset'] - t_runStart
            duration = oriData.loc[t, 'RT_expectation'] if ~np.isnan(oriData.loc[t, 'RT_expectation']) else oriData.loc[t, 'RT_expectation_adj']
            trial_type = 'rating_expectation'
            response_x = oriData.loc[t, 'expectation_end_x']
            response_y = oriData.loc[t, 'expectation_end_y']
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                            "response_x": response_x, "response_y": response_y, \
                            "situation": situation, "context": context, "modality": modality}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)
            
            # Event 5. expectation mouse trajectory
            onset += oriData.loc[t, 'motion_onset_expectation']
            duration = oriData.loc[t, 'motion_dur_expectation']
            trial_type = 'expectation_mouse_trajectory'
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                            "response_x": response_x, "response_y": response_y, \
                            "situation": situation, "context": context, "modality": modality}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)
        
        # change precisions
        precision_dic = {'onset': 3, 'duration': 3}
        newData = newData.round(precision_dic)
        # replace missing values
        newData = newData.replace(np.nan, 'n/a')

        # save new events file
        newFilename = os.path.join(outputDir, sub, 'ses-02', 'func', f'{sub}_ses-02_task-narratives_acq-mb8_run-{run}_events.tsv')
        newData.to_csv(newFilename, sep='\t', index=False)