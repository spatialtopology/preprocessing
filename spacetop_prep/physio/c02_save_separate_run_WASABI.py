#!/usr/bin/env python
"""
save_seperate_run.py
-- Separates .acq files into runs and saves as bids format

Parameters
----------
topdir:
    top directory of physio data
metadata_fname:
    .csv file with subject/session/run information
    Check file in ./demo/spacetop_task-social_run-metadata.csv
slurm_id: int
    if operating on discovery, it would be the job array id
    if operating on local, input an integer, e.g. 1
    if you use a stride of 10, you will be processing the first 10 participants.
stride: int
    how many participants to batch per slurm_id, e.g. 10, 5, 50
sub_zeropad: int
    how many zeros are padded for BIDS subject id
task: str
    specify task name (e.g., 'task-social', 'task-fractional' 'task-alignvideos', 'task-faces', 'task-shortvideos')
run_cutoff: int
    threshold for determining "kosher" runs versus not.
    for instance, task-social is 398 seconds long. We can use the threshold of 300 as a threshold.
    Anything shorter than that is discarded and not converted into a run.
dict_column: dict filepath
    dictionary that changes old column to a new column name.
    json file with key:value as old_column_name:new_column_name.
dict_task: dict filepath
    dictionary that changes old taskname to a new task name.
    json file with key:value as old_task_name:new_task_name.
"""
# %% libraries  _______________________________________________________________________________________________
import argparse
import datetime
import glob
import itertools
import json
import logging
import os
import shutil
import sys
from itertools import compress
from os.path import join
from pathlib import Path

import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd
import seaborn as sns

from spacetop_prep.physio import utils
from spacetop_prep.physio.utils import initialize, preprocess

__author__ = "Heejung Jung, Yaroslav Halchenko"
__copyright__ = "Spatial Topology Project"
__credits__ = [""] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"


def main():

    args = get_args_c02()

    topdir = args.topdir
    metadata_fname = args.metadata
    slurm_id = args.slurm_id # e.g. 1, 2
    stride = args.stride # e.g. 5, 10, 20, 1000
    sub_zeropad = args.sub_zeropad # sub-0016 -> 4
    task = args.task # e.g. 'task-social' 'task-fractional' 'task-alignvideos'
    run_cutoff = args.run_cutoff # e.g. 300
    columnchangefname = args.colnamechange
    tasknamefname = args.tasknamechange
    remove_sub = args.exclude_sub

    # %%
    physio_dir = topdir
    source_dir = join(physio_dir, 'physio02_sort')
    with open(tasknamefname, "r") as read_file:
        dict_task = json.load(read_file)
    with open(columnchangefname, "r") as read_file:
        dict_column = json.load(read_file)

    if dict_task:
        save_dir = join(physio_dir, 'physio03_bids', dict_task[task])
    else:
        save_dir = join(physio_dir, 'physio03_bids', task)
    log_savedir = os.path.join(physio_dir, 'log')

    Path(save_dir).mkdir(parents=True,exist_ok=True )
    Path(log_savedir).mkdir(parents=True,exist_ok=True )

    # set up logger ______________________________________________________________________________________________
    runmeta = pd.read_csv(metadata_fname)
    logger_fname = os.path.join(
        log_savedir, f"biopac_flaglist_{task}_{datetime.date.today().isoformat()}.txt")
    f = open(logger_fname, "w")
    logger = utils.initialize.logger(logger_fname, "physio")

    # %% NOTE: 1. glob acquisition files _________________________________________________________________________
    sub_list = utils.initialize.sublist(source_dir, remove_sub, slurm_id, sub_zeropad, stride)

    acq_list = []
    logger.info(sub_list)
    for sub in sub_list:
        acq = glob.glob(os.path.join(source_dir, sub, "**", f"*{task}*.acq"),
                        recursive=True)
        acq_list.append(acq)
    flat_acq_list = [item for sublist in acq_list  for item in sublist]

    for acq in sorted(flat_acq_list):
    # NOTE: 2. extract information from filenames ________________________________________________________________
        filename = os.path.basename(acq)
        bids_dict = {}
        bids_dict['sub'] = sub  = utils.initialize.extract_bids(filename, 'sub')
        bids_dict['ses'] = ses  = utils.initialize.extract_bids(filename, 'ses')
        bids_dict['task']= task = utils.initialize.extract_bids(filename, 'task')
        # if dict_task:
        #     bids_dict['task'] = dict_task[task]
        #     task = bids_dict['task']


    # NOTE: 3. open physio dataframe (check if exists) ___________________________________________________________
        if os.path.exists(acq):
            main_df, samplingrate = nk.read_acqknowledge(acq)
            logger.info("__________________%s %s __________________", sub, ses)
            logger.info("file exists! -- starting transformation: ")
            main_df.rename(columns=dict_column, inplace=True)
        else:
            logger.error("no biopac file exists")
            continue

    # NOTE: 4. create an mr_aniso channel for MRI RF pulse channel ________________________________________________
        try:
            main_df['mr_aniso'] = main_df['trigger_mri'].rolling(
            window=3).mean()

            ########################
            # FIX:
            # Check if c0-Expression is there, then find a beginning event trigger 
            # If not, Add up event triggers from channels C10-C14 and use those as event triggers 
            main_df['mr_aniso']=main_df['C0-Expression']  # C0-Expression
            
            main_df[] 
            #########################

            
        except:
            logger.error("no MR trigger channel - this was the early days. re run and use the *trigger channel*")
            logger.error(acq)
            continue
    # TST: files without trigger keyword in the acq files should raise exception
        try:
            utils.preprocess.binarize_channel(main_df,
                                            source_col='mr_aniso',
                                            new_col='spike',
                                            threshold=40,
                                            binary_high=5,
                                            binary_low=0)
        except:
            logger.error(f"data is empty - this must have been an empty file or saved elsewhere")
            continue

        dict_spike = utils.preprocess.identify_boundary(main_df, 'spike')
        logger.info("number of spikes within experiment: %d", len(dict_spike['start']))
        main_df['bin_spike'] = 0
        main_df.loc[dict_spike['start'], 'bin_spike'] = 5

    # NOTE: 5. create an mr_aniso channel for MRI RF pulse channel ________________________________________________
        try:
            main_df['mr_aniso_boxcar'] = main_df['trigger_mri'].rolling(
                window=int(samplingrate)).mean()
            mid_val = (np.max(main_df['mr_aniso_boxcar']) -
                    np.min(main_df['mr_aniso_boxcar'])) / 5
            utils.preprocess.binarize_channel(main_df,
                                            source_col='mr_aniso_boxcar',
                                            new_col='mr_boxcar',
                                            threshold=mid_val,
                                            binary_high=5,
                                            binary_low=0)
        except:
            logger.error(f"ERROR:: binarize RF pulse TTL failure - ALTERNATIVE:: use channel trigger instead")
            logger.debug(logger.error)
            continue
        dict_runs = utils.preprocess.identify_boundary(main_df, 'mr_boxcar')
        logger.info("* start_df: %s", dict_runs['start'])
        logger.info("* stop_df: %s", dict_runs['stop'])
        logger.info("* total of %d runs", len(dict_runs['start']))

    # NOTE: 6. adjust one TR (remove it!)_________________________________________________________________________
        sdf = main_df.copy()
        sdf.loc[dict_runs['start'], 'bin_spike'] = 0
        sdf['adjusted_boxcar'] = sdf['bin_spike'].rolling(window=int(samplingrate)).mean()
        mid_val = (np.max(sdf['adjusted_boxcar']) -
                np.min(sdf['adjusted_boxcar'])) / 4
        utils.preprocess.binarize_channel(sdf,
                                        source_col='adjusted_boxcar',
                                        new_col='adjust_run',
                                        threshold=mid_val,
                                        binary_high=5,
                                        binary_low=0)
        dict_runs_adjust = utils.preprocess.identify_boundary(sdf, 'adjust_run')
        logger.info("* adjusted start_df: %s", dict_runs_adjust['start'])
        logger.info("* adjusted stop_df: %s", dict_runs_adjust['stop'])

    # NOTE: 7. identify run transitions ___________________________________________________________________________
        run_list = list(range(len(dict_runs_adjust['start'])))
        try:
            run_bool = ((np.array(dict_runs_adjust['stop'])-np.array(dict_runs_adjust['start']))/samplingrate) > run_cutoff
        except:
            logger.error("start and stop datapoints don't match")
            logger.debug(logger.error)
            continue
        clean_runlist = list(compress(run_list, run_bool))
        shorter_than_threshold_length = list(compress(run_list, ~run_bool))

    # NOTE: 8. save identified runs after cross referencing metadata __________________________________________________________
        if len(shorter_than_threshold_length) > 0:
            logger.info(
                "runs shorter than %d sec: %s %s %s - run number in python order",
                run_cutoff, sub, ses, shorter_than_threshold_length)
        scannote_reference = utils.initialize.subset_meta(runmeta, sub, ses)
        
        meta_runlist = [col for col in scannote_reference if col.startswith('run')]
        print(f"meta_runlist: {meta_runlist}")
        if len(meta_runlist) == len(clean_runlist):
            ref_dict = scannote_reference.to_dict('list')
            run_basename = f"{sub}_{ses}_{task}_CLEAN_RUN-TASKTYLE_recording-ppg-eda_physio.csv"
            # main_df.rename(columns=dict_column, inplace=True)
            main_df_drop = main_df[main_df.columns.intersection(list(dict_column.values()))]
            utils.initialize.assign_runnumber(ref_dict, clean_runlist, dict_runs_adjust, main_df_drop, save_dir,run_basename,bids_dict)
            logger.info("__________________ :+: FINISHED :+: __________________")
        # else:
        #     logger.error(f"number of complete runs do not match scan notes")
        #     logger.error("clean_runlist: %s, scannote_reference.columns: %s", clean_runlist, scannote_reference.columns)
        #     logger.debug(logger.error)

def get_args_c02():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topdir",
                        type=str, help="top directory of physio data", required = True)
    parser.add_argument("-m", "--metadata",
                        type=str, help="filepath to run completion metadata", required = True)
    parser.add_argument("-sid", "--slurm_id",
                        type=int, help="specify slurm array id", required = True)
    parser.add_argument("--stride",
                        type=int, help="how many participants to batch per jobarray")
    parser.add_argument("-z", "--sub-zeropad",
                        type=int, help="how many zeros are padded for BIDS subject id", required = True)
    parser.add_argument("-t", "--task",
                        type=str, help="specify task name (e.g. task-alignvideos)", required = True)
    parser.add_argument("-c", "--run-cutoff",
                        type=int, help="specify cutoff threshold for distinguishing runs (in seconds)", required = True)
    parser.add_argument("--colnamechange",
                        type=str, help="to change column name within .acq file. provide json file with key:value as old_column_name:new_column_name",
                        required = False)
    parser.add_argument("--tasknamechange",
                        type=str, help="to change task name. provide json file with key:value as old_task_name:new_task_name",
                        required = False)
    parser.add_argument('--exclude-sub', nargs='+',
                        type=int, help="string of integers, subjects to be removed from code", required=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
