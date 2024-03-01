# Generate events files for task-faces

# This script reads raw behavior data files from d_beh for task-faces, extracts time stamps and design information, and stores them in new *events.tsv files accompanying BOLD files.

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
taskname = 'task-faces'
session = 'ses-02'

for sub in subList:
    # determine rating type 
    if int(sub[-4:])%2 == 0:
        runDict = {'run-01': 'age', 'run-02': 'sex', 'run-03': 'intensity'}
    else:
        runDict = {'run-01': 'intensity', 'run-02': 'sex', 'run-03': 'age'}

    for run in runDict:
        dataFile = os.path.join(behDataDir, sub, taskname, f'{sub}_{session}_{taskname}_{run}-{runDict[run]}_beh-preproc.csv')
        if not os.path.isfile(dataFile):
            print(f'No file for {sub}_{run}')
            continue
        
        oriData = pd.read_csv(dataFile)
        newData = pd.DataFrame(columns=["onset", "duration", "trial_type", 
                                "response_value", "rating_type",
                                "expression", "sex", "race", "age", "stim_file"])    # new events to store
        
        t_runStart = oriData.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

        for t in range(len(oriData)):    # each trial
            # Event 1. face video playing
            onset = oriData.loc[t, 'event02_face_onset'] - t_runStart
            duration = oriData.loc[t, 'event03_rating_displayonset'] - oriData.loc[t, 'event02_face_onset']
            trial_type = 'face'
            stim_file = oriData.loc[t, 'param_video_filename']
            conditions = stim_file.split('_')
            stim_file = taskname + '/' + stim_file
            rating_type = runDict[run]
            expression = conditions[0][1:].lower()
            sex = conditions[2][1:].lower()
            race = conditions[3][1:]
            age = conditions[4][1:-4].lower()
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "rating_type": rating_type, 'expression': expression, 'sex': sex, \
                                "race": race, "age": age, 'stim_file': stim_file}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)

            # Event 2. rating
            onset = oriData.loc[t, 'event03_rating_displayonset'] - t_runStart
            duration = oriData.loc[t, 'event03_rating_RT'] if ~np.isnan(oriData.loc[t, 'event03_rating_RT']) else oriData.loc[t, 'RT_adj']
            trial_type = 'rating'
            response_value = oriData.loc[t, 'rating_converted']
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "rating_type": rating_type, \
                                'expression': expression, 'sex': sex, "race": race, "age": age}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)
            
            # Event 3. rating mouse trajectory
            onset += oriData.loc[t, 'motion_onset']
            duration = oriData.loc[t, 'motion_dur']
            trial_type = 'rating_mouse_trajectory'
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "rating_type": rating_type, \
                                'expression': expression, 'sex': sex, "race": race, "age": age}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)
        
        # change precisions
        precision_dic = {'onset': 3, 'duration': 3, 'response_value': 4}
        newData = newData.round(precision_dic)
        
        # replace missing values
        newData = newData.replace(np.nan, 'n/a')

        # save new events file
        newFilename = os.path.join(outputDir, sub, session, 'func', f'{sub}_{session}_{taskname}_acq-mb8_{run}_events.tsv')
        newData.to_csv(newFilename, sep='\t', index=False)