# Generate events files for task-shortvideos

# This script reads raw behavior data files from d_beh for task-shortvideos, extracts time stamps and design information, and stores them in new *events.tsv files accompanying BOLD files.

# For more information, please see README.md and the associated paper (Jung et al., 2024)

import os
import glob
import pandas as pd
import numpy as np
import math

# please change `behDataDir` to the top level of the `d_beh` directory
>>>
behDataDir = ''
# please change `outputDir` to the top level of the BIDS directory
>>>
outputDir = ''

# get a list of subjects with available data
folders = glob.glob(os.path.join(outputDir, 'sub-*'))
subList = [os.path.basename(x) for x in folders]
taskname = 'task-shortvideos'
session = 'ses-03'

run = '01'
xcenter = 980
ycenter = 707    # starting point and center point of the rating

for sub in subList: 
    dataFile = os.path.join(behDataDir, sub, taskname, f'{sub}_{session}_{taskname}_beh-preproc.csv')
    if not os.path.isfile(dataFile):
        print(f'No behavior data file for {sub}_run-{run}')
        continue
    
    oriData = pd.read_csv(dataFile)
    newData = pd.DataFrame(columns=["onset", "duration", "trial_type", 
                            "response_angle", "response_label",
                            "block_condition", "mentalizing_level", "stim_file"])    # new events to store
    
    t_runStart = oriData.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

    for t in range(len(oriData)):    # each trial
        # Event 1. cue
        if t%3 == 0:
            # every three trials, there will be a cue event
            onset = oriData.loc[t, 'event01_block_cue_onset'] - t_runStart
            duration = oriData.loc[t, 'event02_video_onset'] - oriData.loc[t, 'event01_block_cue_onset']
            trial_type = 'cue'
            block_condition = oriData.loc[t, 'event01_block_cue_type']
            mentalizing_level = np.nan
            if block_condition == 'mentalizing':
                # only for mentalizing blocks we need to fill in specific conditions
                mentalizing_level = oriData.loc[t, 'event03_rating_type']
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                            "block_condition": block_condition, "mentalizing_level": mentalizing_level}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)

        # Event 2. video playing
        onset = oriData.loc[t, 'event02_video_onset'] - t_runStart
        duration = oriData.loc[t, 'event02_video_stop'] - oriData.loc[t, 'event02_video_onset']
        trial_type = 'video'
        stim_file = oriData.loc[t, 'event02_video_filename']
        stim_file = taskname + '/' + stim_file
        newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                            "block_condition": block_condition, "mentalizing_level": mentalizing_level, "stim_file": stim_file}, index=[0])
        newData = pd.concat([newData, newRow], ignore_index=True)

        # Even 3. rating
        onset = oriData.loc[t, 'event03_rating_displayonset'] - t_runStart
        duration = oriData.loc[t, 'event03_rating_RT'] if ~np.isnan(oriData.loc[t, 'event03_rating_RT']) else oriData.loc[t, 'RT_adj']
            # if there is no response, use the imputed RT 
        trial_type = 'rating'
        x = oriData.loc[t, 'rating_end_x']
        y = oriData.loc[t, 'rating_end_y']
        # calculating angles of ratings and corresponding labels
        if x > xcenter:
            response_angle = math.atan((ycenter-y)/(x-xcenter))
            response_angle = math.pi - response_angle
        elif x == xcenter:
            response_angle = math.pi/2
        else:
            response_angle = math.atan((ycenter-y)/(xcenter-x))
        response_angle = 180*response_angle/math.pi
        if response_angle == 0:
            response_label = 'No sensation'
        elif response_angle <= 3:
            response_label = 'Barely detectable'
        elif response_angle <= 10:
            response_label = 'Weak'
        elif response_angle <= 29:
            response_label = 'Moderate'
        elif response_angle <= 64:
            response_label = 'Strong'
        elif response_angle <= 98:
            response_label = 'Very strong'
        elif response_angle <= 180:
            response_label = 'Strongest possible'
        newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                        "response_angle": response_angle, "response_label": response_label, \
                        "block_condition": block_condition, "mentalizing_level": mentalizing_level}, index=[0])
        newData = pd.concat([newData, newRow], ignore_index=True)
        
        # Event 4. rating mouse trajectory
        onset += oriData.loc[t, 'motion_onset']
        duration = oriData.loc[t, 'motion_dur']
        trial_type = 'rating_mouse_trajectory'
        newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                        "response_angle": response_angle, "response_label": response_label, \
                        "block_condition": block_condition, "mentalizing_level": mentalizing_level}, index=[0])
        newData = pd.concat([newData, newRow], ignore_index=True)
    
    # change precisions
    precision_dic = {'onset': 3, 'duration': 3, 'response_angle': 2}
    newData = newData.round(precision_dic)
    # replace missing values
    newData = newData.replace(np.nan, 'n/a')

    # save new events file
    newFilename = os.path.join(outputDir, sub, session, 'func', f'{sub}_{session}_{taskname}_acq-mb8_run-01_events.tsv')
    newData.to_csv(newFilename, sep='\t', index=False)