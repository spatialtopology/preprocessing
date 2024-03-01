import os, glob, json, math
import pandas as pd
import numpy as np
import math
from os.path import join

outputDir = 'C:\\Users\\f006fkn\\Desktop\\dataPaper\\events_files'
behDataDir = 'C:\\Users\\f006fkn\\Desktop\\dataPaper\\d_beh'

bids_dir = '/Users/h/Documents/projects_local/1076_spacetop' # the top directory of datalad
code_dir = '/Users/h/Documents/projects_local/1076_spacetop/code' # where this code live
source_dir = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata'# where the source behavioral directory lives
beh_inputdir = join(source_dir, 'd_beh')

# get a list of subjects with behavior data
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
        print(f'No file for {sub}_run-{run}')
        continue
    
    oriData = pd.read_csv(dataFile)
    newData = pd.DataFrame(columns=["onset", "duration", "event_type", 
                            "response_angle", "response_label",
                            "selfreference_condition", "mentalizing_level", "stim_file"])    # new events to store
    
    t_runStart = oriData.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

    for t in range(len(oriData)):    # each trial
        # cue
        if t%3 == 0:
            onset = oriData.loc[t, 'event01_block_cue_onset'] - t_runStart
            duration = oriData.loc[t, 'event02_video_onset'] - oriData.loc[t, 'event01_block_cue_onset']
            event_type = 'cue'
            selfreference_condition = oriData.loc[t, 'event01_block_cue_type']
            mentalizing_level = np.nan
            if selfreference_condition == 'mentalizing':
                mentalizing_level = oriData.loc[t, 'event03_rating_type']
            newRow = pd.DataFrame({"onset": onset, "duration": duration, "event_type": event_type, \
                            "selfreference_condition": selfreference_condition, "mentalizing_level": mentalizing_level}, index=[0])
            newData = pd.concat([newData, newRow], ignore_index=True)

        # video playing
        onset = oriData.loc[t, 'event02_video_onset'] - t_runStart
        duration = oriData.loc[t, 'event02_video_stop'] - oriData.loc[t, 'event02_video_onset']
        event_type = 'video'
        stim_file = oriData.loc[t, 'event02_video_filename']
        stim_file = taskname + '/' + stim_file
        newRow = pd.DataFrame({"onset": onset, "duration": duration, "event_type": event_type, \
                            "selfreference_condition": selfreference_condition, "mentalizing_level": mentalizing_level, "stim_file": stim_file}, index=[0])
        newData = pd.concat([newData, newRow], ignore_index=True)

        # rating
        onset = oriData.loc[t, 'event03_rating_displayonset'] - t_runStart
        duration = oriData.loc[t, 'event03_rating_RT']
        event_type = 'rating'
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
        newRow = pd.DataFrame({"onset": onset, "duration": duration, "event_type": event_type, \
                        "response_angle": response_angle, "response_label": response_label, \
                        "selfreference_condition": selfreference_condition, "mentalizing_level": mentalizing_level}, index=[0])
        newData = pd.concat([newData, newRow], ignore_index=True)
        
        # rating_motion
        onset += oriData.loc[t, 'motion_onset']
        duration = oriData.loc[t, 'motion_dur']
        event_type = 'rating_mouse_trajectory'
        newRow = pd.DataFrame({"onset": onset, "duration": duration, "event_type": event_type, \
                        "response_angle": response_angle, "response_label": response_label, \
                        "selfreference_condition": selfreference_condition, "mentalizing_level": mentalizing_level}, index=[0])
        newData = pd.concat([newData, newRow], ignore_index=True)
    
    # change precisions
    precision_dic = {'onset': 3, 'duration': 3, 'response_angle': 2}
    newData = newData.round(precision_dic)

    # save new events file
    newFilename = os.path.join(outputDir, sub, session, 'func', f'{sub}_{session}_{taskname}_acq-mb8_run-01_events.tsv')
    newData.to_csv(newFilename, sep='\t', index=False)


    dataFile = os.path.join(behDataDir, sub, taskname, f'{sub}_{session}_{taskname}_beh-preproc.csv')
    if not os.path.isfile(dataFile):
        continue

    des_duration = {"Description": "For the 'rating' events, if no response was provided, the duration was set as n/a. If you would like to model the rating period, you can use the maximum time for rating (4 seconds) to replace those missing values."}
    description_eventtype = {"LongName": "Event category", 
                    "Description": "A categorical variable indicating event types within a trial", 
                    "Levels": {
                        "cue": "when the cue of question type was displayed at the start of each block", 
                        "video": "when the video was played in each trial", 
                        "rating": "the rating period", 
                        "rating_mouse_trajectory": "the period when the participant was moving the trackball during the rating", 
                    }}
    description_responseangle = {"LongName": "The angle of the rating", 
                        "Description": "The scale is of a semi-circular shape, and a single value of angle can represent a rating. Here the left most end of the scale was defined as 0 degree, while the right most is 180 degree. Thus, all rating angles were within [0 180]."}
    description_responselabel = {"LongName": "The label of the rating", 
                        "Description": "According to a set of rules (see main texts for details), we assigned each rating a label based on the angle of it."}
    description_selfreference_condition = {"LongName": "The experimental condition of the current block (of three trials)", 
                     "Description": "The value in each Level below is the specific cue used in each type of blocks.", 
                     "Levels": {
                         "likeability": "Consider how much you like this character", 
                         "similarity": "How similar are you to the character?", 
                         "mentalizing": "Consider what the character is thinking"
                     }}
    des_mentalLev = {"LongName": "The specific condition for mentalizing blocks", 
                      "Description": "Seven levels of mentalizing questions were used in the study. This column indicates which level was used if the block is mentalizing. The values in each level below are the questions used for that level.", 
                      "Levels": {"angry": "Was the character feeling angry?", 
                                 "calm": "Was the character feeling calm?", 
                                 "danger": "Did the character feel in danger?", 
                                 "enjoy": "Was the character enjoying themselves?", 
                                 "heights": "Was the character afraid of heights?", 
                                 "remember": "Was the character remembering something?", 
                                 "tired": "Was the character feeling tired?"}}
    des_stimFile = {"LongName": "The name of the stimulus file in this trial"}

    dataToWrite = {"onset":"",
                   "duration": des_duration, 
                   "event_type": description_eventtype, 
                   "response_angle": description_responseangle, 
                   "response_label": description_responselabel,
                   "selfreference_condition": description_selfreference_condition, 
                   "mentalizing_level": des_mentalLev, 
                   "stim_file": des_stimFile}

    newFilename = os.path.join(outputDir, sub, session, 'func', f'{sub}_{session}_{taskname}_acq-mb8_run-{run}_events.json')

    with open(newFilename, 'w') as json_file:
        json.dump(dataToWrite, json_file, indent=4)