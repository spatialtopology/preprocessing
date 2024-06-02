# Generate events files for task-alignvideo

# This script reads raw behavior data files from d_beh for task-alignvideo, extracts time stamps and design information, and stores them in new *events.tsv files accompanying BOLD files.

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

# get a list of subjects with available data
folders = glob.glob(os.path.join(outputDir, 'sub-*'))
subList = [os.path.basename(x) for x in folders]
taskname = 'task-alignvideo'
sessionDict = {'ses-01': 4, 'ses-02': 4, 'ses-03': 3, 'ses-04': 2}    # different sessions have different numbers of runs

for sub in sorted(subList):    
    for session in sessionDict:
        for r in range(sessionDict[session]):
            run = 'run-0' + str(r+1)

            dataFile = os.path.join(behDataDir, sub, taskname, session, f'{sub}_{session}_{taskname}_{run}_beh.csv')
            if not os.path.isfile(dataFile):
                print(f'No behavior data file for {sub}_{session}_{run}')
                continue

            oriData = pd.read_csv(dataFile)
            newData = pd.DataFrame(columns=["onset", "duration", "trial_type", 
                                    "response_value", "stim_file"])    # new events to store
            
            t_runStart = oriData.loc[0, 'param_trigger_onset']    # start time of this run; all onsets calibrated by this

            for t in range(len(oriData)):    # each trial
                # Event 1. stimuli presentation
                onset = oriData.loc[t, 'event01_video_onset'] - t_runStart
                duration = oriData.loc[t, 'event01_video_end'] - oriData.loc[t, 'event01_video_onset']
                trial_type = 'video'
                stim_file = oriData.loc[t, 'param_video_filename']
                stim_file = taskname + '/' + stim_file
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)

                # Event 2. rating01
                onset = oriData.loc[t, 'event02_rating01_onset'] - t_runStart
                duration = oriData.loc[t, 'event02_rating01_RT']
                trial_type = 'rating_relevance'
                response_value = oriData.loc[t, 'event02_rating01_rating']
                if duration == 0:
                    # in the experiment, if participants did not provided ratings, the RT would be 0
                    duration = np.nan
                    response_value = np.nan
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)

                # Event 3. rating02
                onset = oriData.loc[t, 'event02_rating02_onset'] - t_runStart
                duration = oriData.loc[t, 'event02_rating02_RT']
                trial_type = 'rating_happy'
                response_value = oriData.loc[t, 'event02_rating02_rating']
                if duration == 0:
                    duration = np.nan
                    response_value = np.nan
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)

                # Event 4. rating03
                onset = oriData.loc[t, 'event02_rating03_onset'] - t_runStart
                duration = oriData.loc[t, 'event02_rating03_RT']
                trial_type = 'rating_sad'
                response_value = oriData.loc[t, 'event02_rating03_rating']
                if duration == 0:
                    duration = np.nan
                    response_value = np.nan
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)

                # Event 5. rating04
                onset = oriData.loc[t, 'event02_rating04_onset'] - t_runStart
                duration = oriData.loc[t, 'event02_rating04_RT']
                trial_type = 'rating_afraid'
                response_value = oriData.loc[t, 'event02_rating04_rating']
                if duration == 0:
                    duration = np.nan
                    response_value = np.nan
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)

                # Event 6. rating05
                onset = oriData.loc[t, 'event02_rating05_onset'] - t_runStart
                duration = oriData.loc[t, 'event02_rating05_RT']
                trial_type = 'rating_disgusted'
                response_value = oriData.loc[t, 'event02_rating05_rating']
                if duration == 0:
                    duration = np.nan
                    response_value = np.nan
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)

                # Event 7. rating06
                onset = oriData.loc[t, 'event02_rating06_onset'] - t_runStart
                duration = oriData.loc[t, 'event02_rating06_RT']
                trial_type = 'rating_warm'
                response_value = oriData.loc[t, 'event02_rating06_rating']
                if duration == 0:
                    duration = np.nan
                    response_value = np.nan
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)

                # Event 8. rating07
                onset = oriData.loc[t, 'event02_rating07_onset'] - t_runStart
                duration = oriData.loc[t, 'event02_rating07_RT']
                trial_type = 'rating_engaged'
                response_value = oriData.loc[t, 'event02_rating07_rating']
                if duration == 0:
                    duration = np.nan
                    response_value = np.nan
                newRow = pd.DataFrame({"onset": onset, "duration": duration, "trial_type": trial_type, \
                                "response_value": response_value, "stim_file": stim_file}, index=[0])
                newData = pd.concat([newData, newRow], ignore_index=True)
            
            # change precisions
            precision_dic = {'onset': 3, 'duration': 3, 'response_value': 2}
            newData = newData.round(precision_dic)
            # replace nan with "n/a"
            newData = newData.replace(np.nan, 'n/a')

            # save new events file
            try:
                newFilename = os.path.join(outputDir, sub, session, 'func', f'{sub}_{session}_task-alignvideo_acq-mb8_{run}_events.tsv')
                newData.to_csv(newFilename, sep='\t', index=False)
            except:
                print(f"failed to save {sub} {session} {taskname} {run}")
