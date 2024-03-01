import os
import glob
import pandas as pd
import numpy as np
from os.path import join
from pathlib import Path
# outputDir = 'C:\\Users\\f006fkn\\Desktop\\dataPaper\\events_files'
# behDataDir = 'C:\\Users\\f006fkn\\Desktop\\dataPaper\\d_beh'

bids_dir = '/Users/h/Documents/projects_local/1076_spacetop' # the top directory of datalad
code_dir = '/Users/h/Documents/projects_local/1076_spacetop/code' # where this code live
source_dir = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata'# where the source behavioral directory lives
behDataDir = join(source_dir, 'd_beh')
outputDir = bids_dir

# get a list of subjects with behavior data
folders = glob.glob(os.path.join(outputDir, 'sub-*'))
subList = [os.path.basename(x) for x in folders]
taskname = 'task-faces'
session = 'ses-02'

for sub in subList: 
    
    if int(sub[-4:])%2 == 0:    # determine rating type 
        runDict = {'run-01': 'age', 'run-02': 'sex', 'run-03': 'intensity'}
    else:
        runDict = {'run-01': 'intensity', 'run-02': 'sex', 'run-03': 'age'}

    for run in runDict:
        dataFile = os.path.join(behDataDir, sub, taskname, f'{sub}_{session}_{taskname}_{run}-{runDict[run]}_beh-preproc.csv')
        # HJ: What is this? this file name is different from what is being saved
        if not os.path.isfile(dataFile):
            print(f'No file for {sub}_{run}')
            continue
        beh_savedir = join(bids_dir, sub, session, 'beh')
        print(beh_savedir)
        oriData = pd.read_csv(dataFile)
        newData = pd.DataFrame(columns=["onset", "duration", "trial_type", 
                                "rating_value", "rating_type",
                                "expression", "sex", "race", "age", "stim_file"])    # new events to store
        
        t_runStart = oriData.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

        for t in range(len(oriData)):    # each trial
            # video playing
            onset = oriData.loc[t, 'event02_face_onset'] - t_runStart
            duration = oriData.loc[t, 'event03_rating_displayonset'] - oriData.loc[t, 'event02_face_onset']
            trial_type = 'face'
            # stim_file = 
            conditions = stim_file.split('_')
            stim_file = taskname + '/' + oriData.loc[t, 'param_video_filename']
            rating_type = runDict[run]
            expression = conditions[0][1:].lower()
            sex = conditions[2][1:].lower()
            race = conditions[3][1:]
            age = conditions[4][1:-4].lower()
            newRow = pd.DataFrame({"onset": onset, 
                                   "duration": duration, 
                                   "trial_type": trial_type, 
                                   "rating_type": rating_type, 
                                   "expression": expression, 
                                   "sex": sex,                                 "race": race, 
                                   "age": age, 
                                   "stim_file": stim_file}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)

            # rating
            onset = oriData.loc[t, 'event03_rating_displayonset'] - t_runStart
            duration = oriData.loc[t, 'event03_rating_RT']
            trial_type = 'rating'
            rating_value = oriData.loc[t, 'rating_converted']
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "rating_value": rating_value, "rating_type": rating_type, \
                                'expression': expression, 'sex': sex, "race": race, "age": age}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)
            
            # rating_mouse_trajectory
            onset += oriData.loc[t, 'motion_onset']
            duration = oriData.loc[t, 'motion_dur']
            trial_type = 'rating_mouse_trajectory'
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "rating_value": rating_value, "rating_type": rating_type, \
                                'expression': expression, 'sex': sex, "race": race, "age": age}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)
        
        # change precisions
        precision_dic = {'onset': 3, 'duration': 3, 'rating_value': 4}
        newData = newData.round(precision_dic)

        # check rating_value
        if any(newData.rating_value > 1) or any(newData.rating_value < 0):
            print(f"Please check the rating values of {sub}_{run}!")

        # save new events file
        Path(beh_savedir).mkdir( parents=True, exist_ok=True )
        newFilename = os.path.join(beh_savedir, f'{sub}_{session}_{taskname}_acq-mb8_{run}_events.tsv')
        newData.to_csv(newFilename, sep='\t', index=False)