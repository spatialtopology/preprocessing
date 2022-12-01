#!/usr/bin/env python
# encoding: utf-8
"""
# if Glob physiology df / ERROR if physiological doesn’t exist
# Check if we already ran the analysis / if so, abort
# Open physiology df
# Open corresponding behavioral df / ERROR if corresponding behavioral df doesn’t exist
# Clean fixation columns
# Baseline correct
# Extract epochs
# TTL extraction
# 1) binarize TTL channel / ERROR if TTL channel doesn’t have any data and fails to run
# 2) assign TTL based on the event boundary
# filter signal
# extract mean signals
# [x] append task info (PVC) from metadata
# [x] move biopac final data into fmriprep: spacetop_data/data/sub/ses/physio
# [x] move behavioral data preprocessed into fmriprep:  spacetop_data/data/sub/ses/beh
# [x] allow to skip broken files
# [x] allow to skip completed files
"""
# %% library
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

import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd
import utils.checkfiles
import utils.initialize
import utils.preprocess
import utils.ttl_extraction

#from spacetop_prep.physio import utils

__author__ = "Heejung Jung, Isabel Neumann"
__copyright__ = "Spatial Topology Project"
# people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__credits__ = ["Yaroslav Halchenko"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

"""
TODO:
minimize spaghetti
- make two separate functions
1) pain process python function
2) non pain run process python function

ENH:
allow for user to input which channels to use
main channel (stimuli)
boundary channel (cue) (rating)
"""
# pwd = os.getcwd()
# main_dir = Path(pwd).parents[0]
# sys.path.append(os.path.join(main_dir))
# sys.path.insert(0, os.path.join(main_dir))
# print(sys.path)

# %%
parser = argparse.ArgumentParser()
# parser.add_argument("-o", "--operating",
#                     choices=['local', 'discovery'],
#                     help="specify where jobs will run: local or discovery")
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
                    type=str, help=".json file for changing physio data channel names | key:value == old_channel_name:new_channel_name")
parser.add_argument("-sid", "--slurm-id", type=int,
                    help="specify slurm array id")
parser.add_argument("--stride", type=int,
                    help="how many participants to batch per jobarray")
parser.add_argument("-z", "--zeropad",
                    type=int, help="how many zeros are padded for BIDS subject id")
parser.add_argument("-t", "--task",
                    type=str, help="specify task name (e.g. task-alignvideos)")
parser.add_argument("-sr", "--samplingrate", type=int,
                    help="sampling rate of acquisition file")
parser.add_argument("--tonic-epochstart", type=int,
                    help="beginning of epoch")
parser.add_argument("--tonic-epochend", type=int,
                    help="end of epoch")
parser.add_argument("--ttl-index", type=int,
                    help="index of which TTL to use")
args = parser.parse_args()

# operating = args.operating # 'local', 'discovery'
physio_dir = args.input_physiodir
beh_dir = args.input_behdir
log_dir = args.output_logdir
output_savedir = args.output_savedir
metadata = args.metadata
dictchannel_json = args.dictchannel
slurm_id = args.slurm_id  # e.g. 1, 2
stride = args.stride  # e.g. 5, 10, 20, 1000
zeropad = args.zeropad  # sub-0016 -> 4
task = args.task  # e.g. 'task-social' 'task-fractional' 'task-alignvideos'
# run_cutoff = args.run_cutoff # e.g. 300
samplingrate = args.samplingrate  # e.g. 2000
tonic_epoch_start = args.tonic_epochstart
tonic_epoch_end = args.tonic_epochend
ttl_index = args.ttl_index

dict_channel = json.load(open(dictchannel_json))

plt.rcParams['figure.figsize'] = [15, 5]  # Bigger images
plt.rcParams['font.size'] = 14

# %% set parameters
sub_list = []
#biopac_list = next(os.walk(physio_dir))[1]
remove_int = [1, 2, 3, 4, 5, 6]
sub_list = utils.initialize.sublist(
    physio_dir, remove_int, slurm_id, stride=stride, sub_zeropad=zeropad)
ses_list = [1, 3, 4]
run_list = [1, 2, 3, 4, 5, 6]
sub_ses = list(itertools.product(sorted(sub_list), ses_list, run_list))
# """
# # NOTE: TEST ______________________________________
# """

# sub_list = ['sub-0074']; ses_list = [1]; run_list = [1,2,3,4,5,6]
# sub_ses = list(itertools.product(sorted(sub_list), ses_list, run_list))
# log_dir = '/Users/h/Dropbox/projects_dropbox/spacetop_biopac/sandbox'
# physio_dir = '/Users/h/Dropbox/projects_dropbox/spacetop_biopac/sandbox'
# """
# # NOTE: TEST ______________________________________
# """
logger_fname = os.path.join(
    log_dir, f"data-physio_step-03-groupanalysis_{datetime.date.today().isoformat()}.txt")


# %% set up logger _______________________________________________________________________________________

runmeta = pd.read_csv(metadata)
# join(project_dir, "data/spacetop_task-social_run-metadata.csv"))
# TODO: come up with scheme to update logger files
f = open(logger_fname, "w")
logger = utils.initialize.logger(logger_fname, "physio")


def extract_bids(fname):
    entities = dict(
        match.split('-', 1) for match in fname.split('_') if '-' in match)
    sub_num = int(entities['sub'])
    ses_num = int(entities['ses'])
    if 'run' in entities['run'].split('-'):
        run_list = entities['run'].split('-')
        run_list.remove('run')
        run_num = run_list[0]
        run_type = run_list[-1]
    else:
        run_num = int(entities['run'].split('-')[0])
        run_type = entities['run'].split('-')[-1]
    return sub_num, ses_num, run_num, run_type


# %%____________________________________________________________________________________________________
flag = []
for i, (sub, ses_ind, run_ind) in enumerate(sub_ses):

    # NOTE: open physio dataframe (check if exists) __________________________________________________________

    ses = f"ses-{ses_ind:02d}"
    run = f"run-{run_ind:02d}"
    logger.info(
        "__________________%s %s %s__________________", sub, ses, run)
    physio_flist = utils.checkfiles.glob_physio_bids(
        physio_dir, sub, ses, task, run)

    try:
        physio_fpath = physio_flist[0]
    except IndexError:
        logger.error(
            "\t* missing physio file - %s %s %s DOES NOT exist", sub, ses, run)
        continue
    phasic_fname = os.path.basename(physio_fpath)
    bids_dict = {}
    bids_dict['sub'] = sub = utils.initialize.extract_bids(phasic_fname, 'sub')
    bids_dict['ses'] = ses = utils.initialize.extract_bids(phasic_fname, 'ses')
    bids_dict['task'] = task = utils.initialize.extract_bids(
        phasic_fname, 'task')
    bids_dict['run'] = run = f"run-{run_ind:02d}"
    #bids_dict['run'] = run = utils.initialize.extract_bids(phasic_fname, 'run')
    logger.info(bids_dict)
    # sub_num, ses_num, run_num, run_type = _extract_bids(
    #     os.path.basename(physio_fpath))
    logger.info(
        "__________________%s %s %s__________________", sub, ses, run)
    # save_dir = join(project_dir, 'data', 'physio', 'physio02_preproc', sub,
    #             ses)
    # save_dir = join(log_dir, 'data', 'physio', 'physio02_preproc', sub,
    #             ses)
# NOTE: if output derivative already exists, skip loop: __________________________________________________
    # try:
    #     save_dir = join(project_dir, 'data', 'physio', 'physio02_preproc',
    #                     sub, ses)
    #     phasic_fname = f"{sub}_{ses}_*{run}-{run_type}_epochstart-0_epochend-5_physio-scr.csv"
    #     if not os.path.exists(glob.glob(join(save_dir, phasic_fname))[0]):
    #         pass
    # except:
    #     save_dir = join(project_dir, 'data', 'physio', 'physio02_preproc',
    #                     sub, ses)
    #     phasic_fname = f"{sub}_{ses}_*{run}-{run_type}_epochstart-0_epochend-5_physio-scr.csv"
    #     logger.warning(
    #         f"aborting: this job was complete for {sub}_{ses}_{run}_-{run_type}"
    #     )
    #     continue

# NOTE: identify physio file for corresponding sub/ses/run _______________________________________________
    physio_fname = os.path.basename(physio_fpath)
    logger.info({physio_fname})
    task = [match for match in physio_fname.split('_') if "task" in match][0]
    # DEP: physio_df, samplingrate = nk.read_acqknowledge(physio_fpath) output file is pandas
    physio_df = pd.read_csv(physio_fpath, sep='\t')


# NOTE: identify behavioral file for corresponding sub/ses/run ____________________________________
    beh_fpath = glob.glob(
        join(beh_dir, sub, ses,
             f"{sub}_{ses}_task-social_{run}*_beh.csv"))
    try:  # # if len(beh_fpath) != 0:
        beh_fname = beh_fpath[0]
    except IndexError:
        logger.error(
            "missing behavioral file: {sub} {ses} {run} DOES NOT exist")
        continue
    beh_df = pd.read_csv(beh_fname)
    run_type = ([
        match for match in os.path.basename(beh_fname).split('_')
        if "run" in match
    ][0]).split('-')[2]
    print(
        f"__________________ {sub} {ses} {run} {run_type} ____________________")
    metadata_df = beh_df[[
        'src_subject_id', 'session_id', 'param_task_name', 'param_run_num',
        'param_cue_type', 'param_stimulus_type', 'param_cond_type'
    ]]

# NOTE: merge fixation columns (some files look different) handle slight changes in biopac dataframe
    if 'fixation-01' in physio_df.columns:
        physio_df[
            'event_fixation'] = physio_df['fixation-01'] + physio_df['fixation-02']

# NOTE: baseline correct _________________________________________________________________________________
    # 1) extract fixations:
    fix_bool = physio_df['event_fixation'].astype(bool).sum()
    logger.info(
        f"* confirming the number of fixation non-zero timepoints: {fix_bool}")
    logger.info("\t* this amounts to %f seconds", fix_bool/samplingrate)
    # baseline correction method 02: use the fixation period from the entire run
    mask = physio_df['event_fixation'].astype(bool)
    baseline_method02 = physio_df['physio_eda'].loc[
        mask].mean()
    physio_df['EDA_corrected_02fixation'] = physio_df[
        'physio_eda'] - baseline_method02

    logger.info(
        f"* baseline using fixation from entire run: {baseline_method02}")

# %% NOTE: extract epochs ___________________________________________________________________________________
    # dict_channel = {'event_cue': 'event_cue',
    # 'event_expectrating': 'event_expectrating',
    # 'event_stimuli': 'event_stimuli',
    # 'event_actualrating': 'event_actualrating',
    # }
    dict_onset = {}
    for i, (key, value) in enumerate(dict_channel.items()):
        dict_onset[value] = {}

        utils.preprocess._binarize_channel(physio_df,
                                           source_col=key,
                                           new_col=value,
                                           threshold=None,
                                           binary_high=5,
                                           binary_low=0)
        dict_onset[value] = utils.preprocess._identify_boundary(
            physio_df, value)
        logger.info("\t* total number of %s trials: %d",
                    value, len(dict_onset[value]['start']))


# %% NOTE: TTL extraction ___________________________________________________________________________________
    if run_type == 'pain':
        final_df = pd.DataFrame()
        # binarize TTL channels (raise error if channel has no TTL, despite being a pain run)
        metadata_df, plateau_start = utils.ttl_extraction.ttl_extraction(
            physio_df=physio_df,
            dict_beforettl=dict_onset['event_expectrating'],
            dict_afterttl=dict_onset['event_actualrating'],
            dict_stimuli=dict_onset['event_stimuli'],
            samplingrate=samplingrate,
            metadata_df=metadata_df,
            ttl_index=ttl_index
        )

        # create a dictionary for neurokit. this will serve as the events
        event_stimuli = {
            'onset': np.array(plateau_start).astype(pd.Int64Dtype),
            'duration': np.repeat(samplingrate * 5, 12),
            'label': np.array(np.arange(12)),
            'condition': metadata_df['param_stimulus_type'].values.tolist()
        }
        # TODO: interim plot to check if TTL matches with signals
        run_physio = physio_df[[
            'EDA_corrected_02fixation', 'physio_ppg', 'trigger_heat'
        ]]
        # run_physio
        # stim_plot = nk.events_plot(event_stimuli, run_physio)
        # TODO: plot and save
    else:
        event_stimuli = {
            'onset': np.array(dict_onset['event_stimuli']['start']),
            'duration': np.repeat(samplingrate * 5, 12),
            'label': np.array(np.arange(12), dtype='<U21'),
            'condition': beh_df['param_stimulus_type'].values.tolist()
        }
        # TODO: plot the ttl and visulize the alignment
        # interim plot to check if TTL matches with signals
        run_physio = physio_df[[
            'EDA_corrected_02fixation', 'physio_ppg', 'event_stimuli'
        ]]
        # run_physio
        stim_plot = nk.events_plot(event_stimuli, run_physio)

# NOTE: neurokit analysis :+: HIGHLIGHT :+: filter signal ________________________________________________

    # IF you want to use raw signal
    # eda_signal = nk.signal_sanitize(run_physio["physio_eda"])
    # eda_raw_plot = plt.plot(run_df["physio_eda"])

# NOTE: PHASIC_____________________________________________________________________________
    amp_min = 0.01
    scr_signal = nk.signal_sanitize(
        physio_df['physio_eda'])
    scr_filters = nk.signal_filter(scr_signal,
                                   sampling_rate=samplingrate,
                                   highcut=1,
                                   method="butterworth",
                                   order=2)  # ISABEL: Detrend
    scr_detrend = nk.signal_detrend(scr_filters)
    # scl_resampled = nk.signal_resample(
        # scr_detrend,  method='interpolation', sampling_rate=2000, desired_sampling_rate=resample_rate)

    scr_decomposed = nk.eda_phasic(nk.standardize(scr_detrend),
                                   sampling_rate=samplingrate)

    scr_peaks, info = nk.eda_peaks(scr_decomposed["EDA_Phasic"].values,
                                   sampling_rate=samplingrate,
                                   method="neurokit",
                                   amplitude_min=amp_min)
    scr_signals = pd.DataFrame({
        "EDA_Raw": scr_signal,
        "EDA_Clean": scr_filters
    })
    scr_processed = pd.concat([scr_signals, scr_decomposed, scr_peaks], axis=1)
    try:
        scr_epochs = nk.epochs_create(scr_processed,
                                      event_stimuli,
                                      sampling_rate=samplingrate,
                                      epochs_start=0,
                                      epochs_end=5,
                                      baseline_correction=True)  #
    except:
        logger.info("has NANS in the dataframe")
        continue
    scr_phasic = nk.eda_eventrelated(scr_epochs)

# NOTE:  TONIC ________________________________________________________________________________
    # tonic_epoch_start = -1
    # tonic_epoch_end = 8
    resample_rate = 25

    scl_signal = nk.signal_sanitize(physio_df['EDA_corrected_02fixation'])
    scl_filters = nk.signal_filter(scl_signal,
                                   sampling_rate=samplingrate,
                                   highcut=1,
                                   method="butterworth",
                                   order=2)  # ISABEL: Detrend
    scl_detrend = nk.signal_detrend(scl_filters)
    scl_resampled = nk.signal_resample(
        scl_detrend,  method='interpolation', sampling_rate=2000, desired_sampling_rate=resample_rate)
    event_stimuli_copy = event_stimuli['onset']
    event_stimuli['onset'] = event_stimuli_copy/(samplingrate/resample_rate)
    scl_decomposed = nk.eda_phasic(nk.standardize(scl_detrend),
                                   sampling_rate=samplingrate)
    scl_signals = pd.DataFrame({
        "EDA_Raw": scl_signal,
        "EDA_Clean": scl_filters
    })
    scl_processed = pd.concat([scl_signals, scl_decomposed['EDA_Tonic']],
                              axis=1)
    try:
        scl_raw = nk.epochs_create(scl_resampled,
                                   event_stimuli,
                                   sampling_rate=resample_rate,
                                   epochs_start=tonic_epoch_start,
                                   epochs_end=tonic_epoch_end,
                                   baseline_correction=False)
    except:
        logger.info("has NANS in the dataframe")
        continue
#  NOTE: concatenate dataframes __________________________________________________________________________
    # TODO: create internal function
    # Make it more flexible for selecting which columns to visualize
    if run_type == 'pain':
        bio_df = pd.concat([
            physio_df[[
                'trigger_mri', 'event_fixation', 'event_cue', 'event_expectrating', 'event_stimuli', 'event_actualrating',
                'trigger_heat'
            ]], scr_processed
        ],
            axis=1)
    else:
        bio_df = pd.concat([
            physio_df[[
                'trigger_mri', 'event_fixation', 'event_cue', 'event_expectrating', 'event_stimuli', 'event_actualrating',
            ]], scr_processed
        ],
            axis=1)
    # TODO: find a way to save neurokit plots
    # fig_save_dir = join(project_dir, 'data', 'physio', 'qc', sub, ses)
    #Path(fig_save_dir).mkdir(parents=True, exist_ok=True)
    #fig_savename = f"{sub}_{ses}_{run}-{run_type}_physio-scr-scl.png"
    # processed_fig = nk.events_plot(
    #     event_stimuli,
    #     bio_df[['administer', 'EDA_Tonic', 'EDA_Phasic', 'SCR_Peaks']])
    # plt.show()
    # TODO: plot save
    # Tonic level ______________________________________________________________________________________
    # 1. append columns to the begining (trial order, trial type)
    # NOTE: eda_epochs_level -> scl_raw
    metadata_tonic = pd.DataFrame(
        index=list(range(len(scl_raw))),
        columns=['trial_order', 'iv_stim', 'mean_signal'])
    try:
        for ind in range(len(scl_raw)):
            metadata_tonic.iloc[
                ind, metadata_tonic.columns.
                get_loc('mean_signal')] = scl_raw[ind]["Signal"].mean()
            metadata_tonic.iloc[
                ind, metadata_tonic.columns.
                get_loc('trial_order')] = scl_raw[ind]['Label'].unique()[0]
            metadata_tonic.iloc[
                ind, metadata_tonic.columns.
                get_loc('iv_stim')] = scl_raw[ind]["Condition"].unique()[0]
    except:
        for ind in range(len(scl_raw)):
            metadata_tonic.iloc[
                ind,
                metadata_tonic.columns.get_loc('mean_signal')] = scl_raw[str(
                    ind)]["Signal"].mean()
            metadata_tonic.iloc[
                ind,
                metadata_tonic.columns.get_loc('trial_order')] = scl_raw[str(
                    ind)]['Label'].unique()[0]
            metadata_tonic.iloc[
                ind, metadata_tonic.columns.get_loc('iv_stim')] = scl_raw[
                    str(ind)]["Condition"].unique()[0]
    # 2. eda_level_timecourse
    tonic_length = np.abs(tonic_epoch_start-tonic_epoch_end) * resample_rate
    eda_level_timecourse = pd.DataFrame(
        index=list(range(len(scl_raw))),
        columns=['time_' + str(col) for col in list(np.arange(resample_rate * np.abs(tonic_epoch_end-tonic_epoch_start)))])
    try:
        for ind in range(len(scl_raw)):
            eda_level_timecourse.iloc[
                ind, :] = scl_raw[ind]['Signal'].to_numpy().reshape(
                    1, resample_rate * np.abs(tonic_epoch_end-tonic_epoch_start)
            )
    except:
        for ind in range(len(scl_raw)):
            eda_level_timecourse.iloc[
                ind, :] = scl_raw[ind]['Signal'].to_numpy().reshape(
                    1, tonic_length
            )
    tonic_df = pd.concat([metadata_df, metadata_tonic], axis=1)
    tonic_timecourse = pd.concat(
        [metadata_df, metadata_tonic, eda_level_timecourse], axis=1)
# NOTE: save tonic data __________________________________________________________________________________
    tonic_save_dir = join(output_savedir, 'physio01_SCL', sub, ses)
    Path(tonic_save_dir).mkdir(parents=True, exist_ok=True)
    tonic_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_epochstart-{tonic_epoch_start}_epochend-{tonic_epoch_end}_physio-scl.csv"
    tonictime_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_epochstart-{tonic_epoch_start}_epochend-{tonic_epoch_end}_physio-scltimecourse.csv"
    tonic_df.to_csv(join(tonic_save_dir, tonic_fname))
    tonic_timecourse.to_csv(join(tonic_save_dir, tonictime_fname))

# NOTE: save phasic data _________________________________________________________________________________
    phasic_save_dir = join(output_savedir, 'physio02_SCR', sub, ses)
    Path(phasic_save_dir).mkdir(parents=True, exist_ok=True)
    metadata_df = metadata_df.reset_index(drop=True)
    scr_phasic = scr_phasic.reset_index(drop=True)
    phasic_meta_df = pd.concat(
        [metadata_df, scr_phasic], axis=1
    )
    phasic_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_epochstart-0_epochend-5_physio-scr.csv"
    phasic_meta_df.to_csv(join(phasic_save_dir, phasic_fname))
    logger.info("__________________ :+: FINISHED :+: __________________")
