#!/usr/bin/env python
# encoding: utf-8

# ----------------------------------------------------------------------
#                               libraries
# ----------------------------------------------------------------------
import argparse
import datetime
import glob
import itertools
import json
import logging
import os
import sys
from os.path import join
from pathlib import Path
from statistics import mean
from tkinter import Variable
from typing import Optional

import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd

import spacetop_prep.physio.utils.checkfiles
from spacetop_prep.physio import utils

print(utils.checkfiles)
print(utils.checkfiles.glob_physio_bids)
print(utils.initialize.sublist)
__author__ = "Heejung Jung, Yaroslav Halchenko, Isabel Neumann"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Yaroslav Halchenko"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

# %%
def main():

# ----------------------------------------------------------------------
#                               parameters
# ----------------------------------------------------------------------
    args = get_args()

    # physio_dir = args.input_physiodir
    # beh_dir = args.input_behdir
    # log_dir = args.output_logdir
    # output_savedir = args.output_savedir
    # metadata = args.metadata
    # dictchannel_json = args.dictchannel
    # slurm_id = args.slurm_id  # e.g. 1, 2
    # stride = args.stride  # e.g. 5, 10, 20, 1000
    # zeropad = args.zeropad  # sub-0016 -> 4
    # task = args.task  # e.g. 'task-social' 'task-fractional' 'task-alignvideos'
    # samplingrate = args.samplingrate  # e.g. 2000
    # SCL_epoch_start = args.scl_epochstart
    # SCL_epoch_end = args.scl_epochend
    # ttl_index = args.ttl_index
    # baselinecorrect = args.baselinecorrect
    # remove_subject_int = args.exclude_sub

    # args = parser.parse_args()

    physio_dir = args.input_physiodir
    beh_dir = args.input_behdir
    log_dir = args.output_logdir
    output_savedir = args.output_savedir
    metadata = args.metadata
    dictchannel_json = args.dictchannel
    slurm_id = args.slurm_id  # e.g. 1, 2
    slurm_stride = args.slurm_stride  # e.g. 5, 10, 20, 1000
    zeropad = args.bids_zeropad  # sub-0016 -> 4
    task = args.bids_task  # e.g. 'task-social' 'task-fractional' 'task-alignvideos'
    event_name = args.event_name
    prior_event = args.prior_event
    later_event = args.later_event
    source_samplingrate = args.source_samplingrate  # e.g. 2000
    dest_samplingrate = args.dest_samplingrate
    SCL_epoch_start = args.scl_epochstart
    SCL_epoch_end = args.scl_epochend
    ttl_index = args.ttl_index
    baselinecorrect = args.baselinecorrect
    remove_subject_int = args.exclude_sub

# %% -------------------------------------------------------------------
#                 local test
# ----------------------------------------------------------------------
    # sub 73
    # ses 1
    # run 5
    # beh_fname = '/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/physio/utils/tests/sub-0081_ses-01_task-social_run-01-pain_beh.csv'
    # physio_fpath = '/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/physio/utils/tests/sub-0081_ses-01_task-cue_run-01-pain_recording-ppg-eda-trigger_physio.tsv'
    # meta_fname = '/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/physio/utils/tests/spacetop_task-social_run-metadata.csv'
    # dictchannel_json = '/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/physio/p01_channel.json'
    # beh_df = pd.read_csv(beh_fname)
    # physio_df = pd.read_csv(physio_fpath, sep='\t')
    # runmeta = pd.read_csv(meta_fname)
    # physio_flist = '/Users/h/Documents/projects_local/sandbox/physiodata/sub-0081/ses-01/sub-0081_ses-01_task-cue_run-01-pain_recording-ppg-eda-trigger_physio.tsv'
    # source_samplingrate = 2000
    # ttl_index = 2
    # SCL_epoch_end = 20
    # SCL_epoch_start = -3
    # sub_list = ['sub-0081']
    # sub = 'sub-0081'
    # ses = 'ses-01'
    # run_type = 'pain'
    # run ='run-01'
    # log_dir = '/Users/h/Desktop'
    # output_savedir = '/Users/h/Documents/projects_local/sandbox/physioresults'
    # physio_dir = '/Users/h/Documents/projects_local/sandbox/physiodata'
# %% -------------------------------------------------------------------
#                 extract parameters and metadata
# ----------------------------------------------------------------------
    
    dict_channel = json.load(open(dictchannel_json))

    plt.rcParams['figure.figsize'] = [15, 5]  # Bigger images
    plt.rcParams['font.size'] = 14

    # identify subjects _________________________________________________
    sub_list = []
    print(f"remove list: {remove_subject_int}")
    sub_list = utils.initialize.sublist(source_dir=physio_dir,
                                        remove_int=remove_subject_int,
                                        slurm_id=slurm_id,sub_zeropad=zeropad,
                                        stride=slurm_stride)
    print(f"sub list: {sub_list}")
    ses_list = [1, 3, 4]
    run_list = [1, 2, 3, 4, 5, 6]
    sub_ses = list(itertools.product(sorted(sub_list), ses_list, run_list))
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger_fname = os.path.join(log_dir, f"data-physio_step-03-groupanalysis_{datetime.date.today().isoformat()}.txt")

    # set up logger ______________________________________________________
    runmeta = pd.read_csv(metadata)
    # TODO: come up with scheme to update logger files
    f = open(logger_fname, "w")
    logger = utils.initialize.logger(logger_fname, "physio")


# %% -------------------------------------------------------------------
#                   main code for SCL extraction and compiling
# ----------------------------------------------------------------------
    flag = []
    for i, (sub, ses_ind, run_ind) in enumerate(sub_ses):

    # ======= NOTE: 1. open physio dataframe (check if exists) ===================================
        ses = f"ses-{ses_ind:02d}"
        run = f"run-{run_ind:02d}"
        logger.info(
            "__________________%s %s %s__________________", sub, ses, run)
        physio_flist = utils.checkfiles.glob_physio_bids(
            physio_dir, sub, ses, task, run)
        try:
            physio_fpath = physio_flist[0]
            logger.info(physio_fpath)
        except: #  IndexError:
            logger.error(
                "\t* missing physio file - %s %s %s DOES NOT exist", sub, ses, run)
            continue
        physio_fname = os.path.basename(physio_fpath)
        bids_dict = {}
        bids_dict['sub'] = sub = utils.initialize.extract_bids(physio_fname, 'sub')
        bids_dict['ses'] = ses = utils.initialize.extract_bids(physio_fname, 'ses')
        bids_dict['task'] = task = utils.initialize.extract_bids(
            physio_fname, 'task')
        bids_dict['run'] = run = f"run-{run_ind:02d}"


    # ======= NOTE: 2. identify physio file for corresponding sub/ses/run =======================
        physio_fname = os.path.basename(physio_fpath)
        logger.info({physio_fname})
        task = [match for match in physio_fname.split('_') if "task" in match][0]
        physio_df = pd.read_csv(physio_fpath, sep='\t')


    # ======= NOTE: 3. identify behavioral file for corresponding sub/ses/run =====================
        beh_fpath = join(beh_dir, sub, ses,
                 f"{sub}_{ses}_*_{run}*_beh.csv")
        beh_fname = utils.initialize.check_beh_exist(beh_fpath)
        logger.info("beh_fpath: %s", beh_fpath)
        logger.info("beh_fname: %s", beh_fname)
        if beh_fname is None:
            continue
        beh_df = pd.read_csv(beh_fname)
        run_type = utils.initialize.check_run_type(beh_fname)
        logger.info(
            "__________________ %s %s %s %s ____________________", sub, ses, run, run_type)
        metadata_df = beh_df[[
            'src_subject_id', 'session_id', 'param_task_name', 'param_run_num',
            'param_cue_type', 'param_stimulus_type', 'param_cond_type', 'event02_expect_RT', 'event02_expect_angle', 'event04_actual_RT', 'event04_actual_angle'
        ]]


    # ======= NOTE: 4. merge fixation columns (some files look different) handle slight changes in biopac dataframe
        """This was necessary for old spacetop files. I can deprecate this, 
        since we no longer use fixation columns in our analysis
        """
        if 'fixation-01' in physio_df.columns:
            physio_df[
                'event_fixation'] = physio_df['fixation-01'] + physio_df['fixation-02']

    # # DEP: baseline correct _______________________________________________________
    #     # 1) extract fixations:
    #     utils.preprocess.identify_fixation_sec(physio_df, 'event_fixation', 2000)
    #     physio_df_bl = utils.preprocess.baseline_correct(
    #         df=physio_df, raw_eda_col='physio_eda', baseline_col='event_fixation')


    # ======= NOTE: 5. extract epochs based on event transitions ===================================
        dict_onset = {}
        for i, (key, value) in enumerate(dict_channel.items()):
            dict_onset[value] = {}

            utils.preprocess.binarize_channel(physio_df,
                                               source_col=key,
                                               new_col=value,
                                               threshold=None,
                                               binary_high=5,
                                               binary_low=0)
            dict_onset[value] = utils.preprocess.identify_boundary(
                physio_df, value)
            logger.info("\t* total number of %s trials: %d",
                        value, len(dict_onset[value]['start']))
        event_num = len(dict_onset[event_name]['start'])        
        

    # ======= NOTE: 6. event onset extraction ========================================================
        """
        If it's a pain run, it will first extract ttl indices and identify event onsets.
        If not, the code will extract the `event-name` of interest and extract onsets based on boundary conditions.
        """
        if run_type == 'pain':
            final_df = pd.DataFrame()
            # binarize TTL channels (raise error if channel has no TTL, despite being a pain run)
            nan_index, metadf_dropNA, plateau_start, final_df = utils.ttl_extraction.ttl_extraction(
                physio_df=physio_df,
                dict_beforettl=dict_onset[prior_event],
                dict_afterttl=dict_onset[later_event],
                dict_stimuli=dict_onset[event_name],
                samplingrate=source_samplingrate,
                metadata_df=metadata_df,
                ttl_index=ttl_index
            )
            # create a dictionary for neurokit. this will serve as the events
            event_stimuli = {
                'onset': np.array(plateau_start).astype(pd.Int64Dtype),
                'duration': np.repeat(source_samplingrate * 5, len(plateau_start)), # TODO: refactor 5. event_length
                'label': np.array(np.arange(len(plateau_start))),
                'condition': metadf_dropNA['param_stimulus_type'].values.tolist()
            }
            
            event_num = len(dict_onset[event_name]['start'])
            event_length = np.mean(event_stimuli['duration'])

            physio_topdir = Path(physio_dir).parents[0] 
            ttl_dir = join(physio_topdir, 'physio04_ttl', task, sub, ses) # TODO: refactor ttl_dir
            Path(ttl_dir).mkdir(parents=True, exist_ok=True)
            final_df.to_csv(join(ttl_dir, f"{sub}_{ses}_{task}_{run}-pain_recording-medocttl_physio.tsv"))

        else:
            metadf_dropNA =  metadata_df.assign(trial_num=list(np.array(metadata_df.index + 1)))

            event_stimuli = {
                'onset': np.array(dict_onset[event_name]['start']),
                'duration': np.repeat(source_samplingrate * 5, event_num), # TODO: refactor 5. event_length, refactor 12 [x]: event trial number
                'label': np.array(np.arange(event_num), dtype='<U21'),
                'condition': beh_df['param_stimulus_type'].values.tolist()
            }


    # ======= NOTE: 7. save dict_onset ===============================================================
        dict_savedir = join(output_savedir, 'physio01_SCL', sub, ses)
        dict_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_samplingrate-{source_samplingrate}_onset.json"
        utils.preprocess.save_dict(dict_savedir, dict_fname, dict_onset)


    # ======= NOTE: 8. baseline correct ===============================================================
        if baselinecorrect == True:
            baseline_length = source_samplingrate* np.abs(SCL_epoch_start)
            physio_df['physio_eda_blcorrect'] = physio_df['physio_eda']
            #TODO: turn into a shorter function
            for i in range(len(dict_onset[event_name]['start'])):
                if i == 0:
                    baseline_average = []
                    baseline_start_ind = dict_onset[event_name]['start'][i] - baseline_length
                    baseline_stop_ind = dict_onset[event_name]['start'][i]
                    baseline_average = physio_df.loc[baseline_start_ind:baseline_stop_ind]['physio_eda'].mean()
                    # print(baseline_average)
                    start_index = physio_df.index[0]
                    stop_index = dict_onset[event_name]['start'][i+1] - baseline_length
                    # print(start_index, stop_index)
                    physio_df.loc[start_index:stop_index,'physio_eda_blcorrect'] = physio_df.loc[start_index:stop_index]['physio_eda'] - baseline_average
                elif i < len(dict_onset[event_name]['start'])-1:
                    baseline_average = []
                    baseline_start_ind = dict_onset[event_name]['start'][i] - baseline_length
                    baseline_stop_ind = dict_onset[event_name]['start'][i]
                    baseline_average = physio_df.loc[baseline_start_ind:baseline_stop_ind]['physio_eda'].mean()
                    # print(baseline_average)
                    start_index = dict_onset[event_name]['start'][i] - baseline_length
                    stop_index = dict_onset[event_name]['start'][i+1] - baseline_length
                    # print(start_index, stop_index)
                    physio_df.loc[start_index:stop_index,'physio_eda_blcorrect'] = physio_df.loc[start_index:stop_index]['physio_eda'] - baseline_average
                elif i == len(dict_onset[event_name]['start'])-1:
                    baseline_average = []
                    baseline_start_ind = dict_onset[event_name]['start'][i] - baseline_length
                    baseline_stop_ind = dict_onset[event_name]['start'][i]
                    baseline_average = physio_df.loc[baseline_start_ind:baseline_stop_ind]['physio_eda'].mean()
                    # print(baseline_average)
                    start_index = dict_onset[event_name]['start'][i]  - baseline_length
                    stop_index = physio_df.index[-1]
                    # print(start_index, stop_index)
                    physio_df.loc[start_index:stop_index,'physio_eda_blcorrect'] = physio_df.loc[start_index:stop_index]['physio_eda'] - baseline_average
            # TODO: downsample before saving
            resamp = nk.signal_resample(
                physio_df['physio_eda_blcorrect'].to_numpy(),  method='interpolation', sampling_rate=source_samplingrate, desired_sampling_rate=dest_samplingrate)
            edabl_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_epochstart-{SCL_epoch_start}_epochend-{SCL_epoch_end}_baselinecorrect-{baselinecorrect}_samplingrate-{dest_samplingrate}_physio-eda"
            physio_df.to_tsv(join(output_savedir, 'physio01_SCL', sub, ses, edabl_fname + '.tsv'), sep='\t')

            # Plot the selected columns against the index
            plt.plot(physio_df.index, physio_df['physio_eda_blcorrect'], label='Baseline corrected')
            plt.plot(physio_df.index, physio_df['physio_eda'], label='EDA')
            plt.xlabel('time');            plt.ylabel('EDA signal');            plt.legend()
            plt.savefig(physio_df.to_tsv(join(output_savedir, 'physio01_SCL', sub, ses, edabl_fname + '.png')))


    # ======= NOTE: 9. extract TONIC signal  ======================================================================

            # tonic_length, scl_raw, scl_epoch = utils.preprocess.extract_SCL(df=physio_df_bl,
            #                         eda_col='physio_eda_blcorrect', event_dict=event_stimuli, samplingrate=2000,
            #                         SCL_start=SCL_epoch_start, SCL_end=SCL_epoch_end, baseline_truefalse=False)
        # NOTE: filter, detrend, etc depending on customization
        if baselinecorrect == True:
            tonic_length, scl_raw, scl_epoch = utils.preprocess.extract_SCL_custom(
                            df=physio_df,
                            eda_col='physio_eda_blcorrect', 
                            event_dict=event_stimuli, samplingrate=source_samplingrate,
                            SCL_start=SCL_epoch_start, SCL_end=SCL_epoch_end, 
                            baseline_truefalse=False, 
                            highcut_filter=1, 
                            detrend=True)
        elif baselinecorrect == False:
            baseline_length = 0
            tonic_length, scl_raw, scl_epoch = utils.preprocess.extract_SCL_custom(
                df=physio_df,
                eda_col='physio_eda', 
                event_dict=event_stimuli, samplingrate=source_samplingrate,
                SCL_start=SCL_epoch_start, SCL_end=SCL_epoch_end, 
                baseline_truefalse=False, 
                highcut_filter=1, 
                detrend=False)
            

#  ======= NOTE: 10. concatenate dataframes ===============================================================

        # Tonic level ______________________________________________________________________________________

        # 1. append columns to the beginning (trial order, trial type)
        metadata_SCL = utils.preprocess.combine_metadata_SCL(scl_raw, metadf_dropNA, total_trial=event_num)
        # 2. eda_level_timecourse ------------------------------------
        #dest_samplingrate = 25
        tonic_length = np.abs(SCL_epoch_start-SCL_epoch_end) * dest_samplingrate
        """
        using the nan values
        if nan values are not empty
        fill the rating columns with "nan"
        concatenate it back to the metadataframe based on index values.
        """

        if run_type == 'pain' and len(nan_index) > 0:
            try:
                metadata_d = utils.preprocess.substitute_beh_NA(nan_index, metadata_df, ['angle', 'RT'])
                logger.info("preprocess.substitute_beh_NA WORKS")
            except:
                nan_ind = nan_index[0]
                metadata_d = metadf_dropNA.copy()
                metadata_d.loc[nan_ind, metadata_df.columns.str.contains('angle')] = np.nan
                metadata_d.loc[nan_ind, metadata_df.columns.str.contains('RT')] = np.nan
                logger.info("preprocess.substitute_beh_NA BUG")
        elif run_type == 'vicarious' or run_type == 'cognitive':
            metadata_d = metadf_dropNA.copy()
        else:
            metadata_d = metadf_dropNA.copy()
    
        eda_level_timecourse = utils.preprocess.resample_scl2pandas_ver2(scl_output=scl_raw, 
                                                                        metadata_df=metadf_dropNA , 
                                                                        total_trial=event_num, 
                                                                        tonic_length=tonic_length,
                                                                        sampling_rate=source_samplingrate, 
                                                                        desired_sampling_rate=dest_samplingrate)
        SCL_df = pd.concat([metadata_d, metadata_SCL], axis=1)
        tonic_timecourse = pd.concat(
            [metadata_d, metadata_SCL, eda_level_timecourse], axis=1)


    # ======= NOTE: 11. save tonic data ====================================================================================
        tonic_save_dir = join(output_savedir, 'physio01_SCL', sub, ses)
        Path(tonic_save_dir).mkdir(parents=True, exist_ok=True)
        tonic_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_epochstart-{SCL_epoch_start}_epochend-{SCL_epoch_end}_baselinecorrect-{baselinecorrect}_physio-scl.csv"
        tonictime_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_epochstart-{SCL_epoch_start}_epochend-{SCL_epoch_end}_baselinecorrect-{baselinecorrect}_samplingrate-{dest_samplingrate}_ttlindex-{ttl_index}_physio-scltimecourse.csv"
        SCL_df.to_csv(join(tonic_save_dir, tonic_fname), index = False)
        tonic_timecourse.to_csv(join(tonic_save_dir, tonictime_fname), index = False)


    # ======= NOTE: 12. save metadata ===============================================================
        analysis = {"sub":sub, "ses":ses, "run":run, "run_type":run_type, 
                    "samplingrate":source_samplingrate,
                    "event_of_interest":event_name,
                    "event_length":event_length,
                    "event_trialnum":event_num,
                    "highcut_filter":1,
                    "detrend":True,
                    "baselinecorrect":baselinecorrect,
                    "baselinecorrect_interval":baseline_length,
                    }
        logger.info("__________________ :+: FINISHED :+: __________________\n")

# %% -------------------------------------------------------------------
#                        argparse parameters
# ----------------------------------------------------------------------

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-physiodir",
                        type=str, help="path where BIDS converted physio data lives")
    parser.add_argument("--input-behdir",
                        type=str, help="path where BIDS converted behavioral data lives")
    parser.add_argument("--output-logdir",
                        type=str, help="path where logs will be saved - essential for re-running failed participants")
    parser.add_argument("--output-savedir",
                        type=str, help="path where transformed physio data will be saved")
    parser.add_argument("--metadata",
                        type=str, help=".csv filepath to metadata file of run information (complete/runtype etc)")
    parser.add_argument("--dictchannel",
                        type=str,
                        help=".json file for changing physio data channel names | key:value == "
                             "old_channel_name:new_channel_name")
    parser.add_argument("--slurm-id", type=int,
                        help="specify slurm array id")
    parser.add_argument("--slurm-stride", type=int,
                        help="how many participants to batch per jobarray")
    parser.add_argument("--bids-zeropad",
                        type=int, help="how many zeros are padded for BIDS subject id")
    parser.add_argument("--bids-task",
                        type=str, help="specify task name (e.g. task-alignvideos)")
    parser.add_argument("--event-name",
                        type=str, help="specify task name (e.g. event_stimuli)")
    parser.add_argument("--prior-event",
                        type=str, help="specify channel prior to the event name of interest. Purpose: identify boundary conditions")
    parser.add_argument("--later-event",
                        type=str, help="specify channel that comes after the event of interest. Purpose: identify boundary conditions")
    parser.add_argument("--source-samplingrate", type=int,
                        help="sampling rate of acquisition file")
    parser.add_argument("--dest-samplingrate", type=int,
                        help="downsampled sampling rate")
    parser.add_argument("--scl-epochstart", type=int,
                        help="beginning of epoch (e.g. -3 indicates 3 seconds prior to event of interest)")
    parser.add_argument("--scl-epochend", type=int,
                        help="end of epoch (e.g. 20 indicates 20 seconds after onset of event of interest)")
    parser.add_argument("--ttl-index", type=int,
                        help="index of which TTL to use")
    parser.add_argument("--baselinecorrect", type=bool, 
                        help="indicate whether you want to baseline correct our not. Our methods uses how ever many timepoints you extract (SCL_epochstart) prior to event. We calculate the average and subtract that from the signal")
    parser.add_argument('--exclude-sub', nargs='+',
                        type=int, help="string of integers, subjects to be removed from code", required=False)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
