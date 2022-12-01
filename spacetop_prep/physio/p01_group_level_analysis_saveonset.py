#!/usr/bin/env python
# encoding: utf-8
"""

"""
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
# %% libraries _________________________________________________________________________________________
from tkinter import Variable

import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd
import utils.checkfiles
import utils.initialize
import utils.preprocess
from utils import ttl_extraction

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

# %% argument parser _______________________________________________________________________________________
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
samplingrate = args.samplingrate  # e.g. 2000
tonic_epoch_start = args.tonic_epochstart
tonic_epoch_end = args.tonic_epochend
ttl_index = args.ttl_index


# %%
physio_dir,beh_dir,log_dir,output_savedir,metadata, \
    dictchannel_json,slurm_id,stride,zeropad,task,samplingrate, \
    tonic_epoch_start,tonic_epoch_end,ttl_index = utils.initialize.argument_p01()
dict_channel = json.load(open(dictchannel_json))

plt.rcParams['figure.figsize'] = [15, 5]  # Bigger images
plt.rcParams['font.size'] = 14

# %% set parameters
sub_list = []
remove_subject_int = [1, 2, 3, 4, 5, 6]
sub_list = utils.initialize.sublist(
    physio_dir, remove_subject_int, slurm_id, stride=stride, sub_zeropad=zeropad)
ses_list = [1, 3, 4]
run_list = [1, 2, 3, 4, 5, 6]
sub_ses = list(itertools.product(sorted(sub_list), ses_list, run_list))

logger_fname = os.path.join(
    log_dir, f"data-physio_step-03-groupanalysis_{datetime.date.today().isoformat()}.txt")

# set up logger _______________________________________________________________________________________

runmeta = pd.read_csv(metadata)
# TODO: come up with scheme to update logger files
f = open(logger_fname, "w")
logger = utils.initialize.logger(logger_fname, "physio")


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
    logger.info(bids_dict)
    logger.info(
        "__________________%s %s %s__________________", sub, ses, run)

# NOTE: identify physio file for corresponding sub/ses/run _______________________________________________
    physio_fname = os.path.basename(physio_fpath)
    logger.info({physio_fname})
    task = [match for match in physio_fname.split('_') if "task" in match][0]
    # DEP: physio_df, samplingrate = nk.read_acqknowledge(physio_fpath) output file is pandas
    physio_df = pd.read_csv(physio_fpath, sep='\t')


# NOTE: identify behavioral file for corresponding sub/ses/run ____________________________________
# TODO: Ask Yarik
# what's the best way to log errors? within a function?
# or outtside a functiono


    # def glob_corresponding_beh(file2check: str):
    #     """glob specific string and return one behavioral file
    #     TODO: raise error if not existt"""
    #     file2check = glob.glob(
    #         join(beh_dir, sub, ses,
    #              f"{sub}_{ses}_task-social_{run}*_beh.csv"))
    #     beh_fname = file2check[0]
    #     return beh_fname

    def check_beh_exist(file2check: str):
        try:
            beh_glob = glob.glob(file2check)
            beh_fname = beh_glob[0]
            return beh_fname
        except IndexError:
            sub = utils.initialize.extract_bids(file2check, 'sub')
            ses = utils.initialize.extract_bids(file2check, 'ses')
            run = utils.initialize.extract_bids(file2check, 'run')
            logger.error(
                "missing behavioral file: {sub} {ses} {run} DOES NOT exist")

    def check_run_type(beh_fname: str):
        run_type = ([match for match in os.path.basename(
            beh_fname).split('_') if "run" in match][0]).split('-')[2]
        return run_type

    beh_fpath = join(beh_dir, sub, ses,
             f"{sub}_{ses}_task-social_{run}*_beh.csv")
    beh_fname = utils.initialize.check_beh_exist(beh_fpath)
    beh_df = pd.read_csv(beh_fname)
    run_type = utils.initialize.check_run_type(beh_fname)
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
    def identify_fixation_sec(df: pd.DataFrame, baseline_col: str, samplingrate: int):
        """
        identify how many timepointts there are for column to baseline correct

        parameters
        ----------
        df
        baseline_col
        samplingrate

        oritinal code
        ----------
        # logger.info(f"* baseline using fixation from entire run: {baseline}")
        # fix_bool = physio_df['event_fixation'].astype(bool).sum()
        # logger.info(
        #     f"* confirming the number of fixation non-zero timepoints: {fix_bool}")
        # logger.info("\t* this amounts to %f seconds", fix_bool/samplingrate)
        """
        fix_bool = physio_df[baseline_col].astype(bool).sum()
        logger.info(
            f"* confirming the number of fixation non-zero timepoints: {fix_bool}")
        logger.info("\t* this amounts to %f seconds", fix_bool/samplingrate)

    def baseline_correct(df, raw_eda_col: str, baseline_col: str):
        """
        parameters
        ----------
        raw_eda_col: str
            column name for raw eda signal
        baseline_col: sttr
            column name for reference column for baseline correction
        TODO: fix everycolumn name t EDA_baselinecorrected (or something shorter)

        # Original ___________________________________________________________________________________
        # baseline correction method 02: use the fixation period from the entire run
        # mask = physio_df['event_fixation'].astype(bool)
        # baseline_method02 = physio_df['physio_eda'].loc[
        #     mask].mean()
        # physio_df['EDA_corrected_02fixation'] = physio_df[
        #     'physio_eda'] - baseline_method02

        # logger.info(
        #     f"* baseline using fixation from entire run: {baseline_method02}")
        """
        mask = df[baseline_col].astype(bool)
        baseline = df[raw_eda_col].loc[mask].mean()
        df[f"{raw_eda_col}_blcorrect"] = df[raw_eda_col] - baseline
        return df

    utils.preprocess.identify_fixation_sec(physio_df, 'event_fixation', 2000)
    physio_df_bl = utils.preprocess.baseline_correct(
        df=physio_df, raw_eda_col='physio_eda', baseline_col='event_fixation')

    # ___________________________________________________________________________________

# NOTE: extract epochs ___________________________________________________________________________________
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


# NOTE: TTL extraction ___________________________________________________________________________________

    def plot_ttl_extraction(df: pd.DataFrame, list_columns: list, event_stimuli: dict):
        """
        parameters
        ----------
        df: pandas dataframe
        list_columns: list
            list of columns that we want to subplot with event stimuli
        event_stimuli: dict
            dictionary with TTL extracted onset

        original code
        run_physio = physio_df[[
            'EDA_corrected_02fixation', 'physio_ppg', 'trigger_heat'
        ]]
        # run_physio
        # stim_plot = nk.events_plot(event_stimuli, run_physio)
        """
        stim_plot = nk.events_plot(event_stimuli, df[list_columns])
        # TODO: plot and save

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
        plot_ttl_extraction(physio_df, [
                            'EDA_corrected_02fixation', 'physio_ppg', 'trigger_heat'], event_stimuli)

    else:
        event_stimuli = {
            'onset': np.array(dict_onset['event_stimuli']['start']),
            'duration': np.repeat(samplingrate * 5, 12),
            'label': np.array(np.arange(12), dtype='<U21'),
            'condition': beh_df['param_stimulus_type'].values.tolist()
        }
        plot_ttl_extraction(physio_df, [
                            'EDA_corrected_02fixation', 'physio_ppg', 'trigger_heat'], event_stimuli)

# NOTE: save dict_onset __________________________________________________________________________________
    def save_dict(save_dir:str, save_fname:str, dict_onset:dict):
        """
        create save directory
        save dictionary with onsets

        parameter:
        ----------
        save_dir: str
            path to save dictionary
        save_fname: str
            filename
        dict_onset: dict
            full dictionary with event onset times

        original code
        -------------
        dict_savedir = join(output_savedir, 'physio01_SCL', sub, ses)
        Path(dict_savedir).mkdir(parents=True, exist_ok=True)
        dict_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_onset.json"
        out_file = open(dict_fname, "w+")
        json.dump(dict_onset, out_file)
        """
        # dict_savedir = join(output_savedir, 'physio01_SCL', sub, ses)
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        # dict_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_onset.json"
        out_file = open(save_fname, "w+")
        json.dump(dict_onset, out_file)

    dict_savedir = join(output_savedir, 'physio01_SCL', sub, ses)
    dict_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_onset.json"
    utils.preprocess.save_dict(dict_savedir, dict_fname, dict_onset)
# NOTE: neurokit analysis :+: HIGHLIGHT :+: filter signal ________________________________________________

    # IF you want to use raw signal
    # eda_signal = nk.signal_sanitize(run_physio["physio_eda"])
    # eda_raw_plot = plt.plot(run_df["physio_eda"])

# NOTE: PHASIC_____________________________________________________________________________
    def plot_SCRprocessed(df, list_columns, scr_processed, save_dir):
        """
        plot scr processed and save to QC location

        parameters
        ----------
        df: dataframe,
        list_columns: list,
        scr_processed: ,
        save_dir:
        """
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
        fig_save_dir = join(save_dir, 'data', 'physio', 'qc', sub, ses)
        Path(fig_save_dir).mkdir(parents=True, exist_ok=True)

        fig_savename = f"{sub}_{ses}_{run}-{run_type}_physio-scr-scl.png"
        processed_fig = nk.events_plot(
            event_stimuli,
            bio_df[['administer', 'EDA_Tonic', 'EDA_Phasic', 'SCR_Peaks']])
        # plt.show()
        # TODO: plot save

    def extract_SCR(df, eda_col, amp_min, event_stimuli, samplingrate, epochs_start, epochs_end, baseline_correction, plt_col: list, plt_savedir):
        """
        parameters
        ----------
        df: dataframe,

        eda_col:
        -----
        """
        scr_signal = nk.signal_sanitize(
            df[eda_col])
        scr_filters = nk.signal_filter(scr_signal,
                                       sampling_rate=samplingrate,
                                       highcut=1,
                                       method="butterworth",
                                       order=2)  # ISABEL: Detrend
        scr_detrend = nk.signal_detrend(scr_filters)
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
        scr_processed = pd.concat(
            [scr_signals, scr_decomposed, scr_peaks], axis=1)
        plot_SCRprocessed(df, plt_col, scr_processed, plt_savedir)
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
        return scr_phasic
        """
        original code
        -------------
            amp_min = 0.01
            scr_signal = nk.signal_sanitize(
                physio_df['physio_eda'])
            scr_filters = nk.signal_filter(scr_signal,
                                        sampling_rate=samplingrate,
                                        highcut=1,
                                        method="butterworth",
                                        order=2)  # ISABEL: Detrend
            scr_detrend = nk.signal_detrend(scr_filters)

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
        """
    scr_phasic = utils.preprocess.extract_SCR(df=physio_df,
                             eda_col='physio_eda',
                             amp_min=0.01,
                             event_stimuli=event_stimuli, samplingrate=2000,
                             epochs_start=0, epochs_end=5, baseline_correction=True, plot_col=['trigger_mri', 'event_fixation', 'event_cue', 'event_expectrating', 'event_stimuli', 'event_actualrating']
                             )

# NOTE:  TONIC ________________________________________________________________________________
    def extract_SCL(df, eda_col, event_dict, samplingrate, SCL_start, SCL_end, baseline_correction):
        """
        tonic_epoch_start = -1
        tonic_epoch_end = 8
        tonic_length = np.abs(tonic_epoch_start-tonic_epoch_end) * samplingrate
        scl_signal = nk.signal_sanitize(physio_df['EDA_corrected_02fixation'])
        scl_filters = nk.signal_filter(scl_signal,
                                    sampling_rate=samplingrate,
                                    highcut=1,
                                    method="butterworth",
                                    order=2)  # ISABEL: Detrend
        scl_detrend = nk.signal_detrend(scl_filters)
        scl_decomposed = nk.eda_phasic(nk.standardize(scl_detrend),
                                    sampling_rate=samplingrate)
        scl_signals = pd.DataFrame({
            "EDA_Raw": scl_signal,
            "EDA_Clean": scl_filters
        })
        scl_processed = pd.concat([scl_signals, scl_decomposed['EDA_Tonic']],
                                axis=1)
        try:
            scl_epoch = nk.epochs_create(scl_processed['EDA_Tonic'],
                                        event_stimuli,
                                        sampling_rate=samplingrate,
                                        epochs_start=tonic_epoch_start,
                                        epochs_end=tonic_epoch_end,
                                        baseline_correction=False)
        except:
            logger.info("has NANS in the dataframe")
            continue
        """
        # tonic_epoch_start = -1
        # tonic_epoch_end = 8
        tonic_length = np.abs(SCL_start-SCL_end) * samplingrate
        scl_signal = nk.signal_sanitize(df[eda_col])
        scl_filters = nk.signal_filter(scl_signal,
                                       sampling_rate=samplingrate,
                                       highcut=1,
                                       method="butterworth",
                                       order=2)  # ISABEL: Detrend
        scl_detrend = nk.signal_detrend(scl_filters)
        scl_decomposed = nk.eda_phasic(nk.standardize(scl_detrend),
                                       sampling_rate=samplingrate)
        scl_signals = pd.DataFrame({
            "EDA_Raw": scl_signal,
            "EDA_Clean": scl_filters
        })
        scl_processed = pd.concat([scl_signals, scl_decomposed['EDA_Tonic']],
                                  axis=1)
        try:
            scl_epoch = nk.epochs_create(scl_processed['EDA_Tonic'],
                                         event_dict,
                                         sampling_rate=samplingrate,
                                         epochs_start=SCL_start,
                                         epochs_end=SCL_end,
                                         baseline_correction=baseline_correction_tf)
            return tonic_length, scl_epoch
        except:
            logger.info("has NANS in the dataframe")
            continue

    tonic_length, scl_epoch = utils.preprocess.extract_SCL(df=physio_df_bl,
                            eda_col='physio_eda_blcorrected', event_dict=event_stimuli, samplingrate=2000,
                            SCL_start=tonic_epoch_start, SCL_end=tonic_epoch_end, baseline_correction_tf=False)

#  NOTE: concatenate dataframes __________________________________________________________________________

    # Tonic level ______________________________________________________________________________________

    # 1. append columns to the begining (trial order, trial type)
    # NOTE: eda_epochs_level -> scl_epoch
    def combine_metadata_SCL(scl_epoch):
        """
        parameters
        ----------
        original code
        -------------
        metadata_tonic = pd.DataFrame(
        index=list(range(len(scl_epoch))),
        columns=['trial_order', 'iv_stim', 'mean_signal'])
        try:
            for ind in range(len(scl_epoch)):
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.
                    get_loc('mean_signal')] = scl_epoch[ind]["Signal"].mean()
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.
                    get_loc('trial_order')] = scl_epoch[ind]['Label'].unique()[0]
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.
                    get_loc('iv_stim')] = scl_epoch[ind]["Condition"].unique()[0]
        except:
            for ind in range(len(scl_epoch)):
                metadata_tonic.iloc[
                    ind,
                    metadata_tonic.columns.get_loc('mean_signal')] = scl_epoch[str(
                        ind)]["Signal"].mean()
                metadata_tonic.iloc[
                    ind,
                    metadata_tonic.columns.get_loc('trial_order')] = scl_epoch[str(
                        ind)]['Label'].unique()[0]
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.get_loc('iv_stim')] = scl_epoch[
                        str(ind)]["Condition"].unique()[0]
        ---
        """
        metadata_tonic = pd.DataFrame(
        index=list(range(len(scl_epoch))),
        columns=['trial_order', 'iv_stim', 'mean_signal'])
        try:
            for ind in range(len(scl_epoch)):
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.
                    get_loc('mean_signal')] = scl_epoch[ind]["Signal"].mean()
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.
                    get_loc('trial_order')] = scl_epoch[ind]['Label'].unique()[0]
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.
                    get_loc('iv_stim')] = scl_epoch[ind]["Condition"].unique()[0]
            return metadata_tonic
        except:
            for ind in range(len(scl_epoch)):
                metadata_tonic.iloc[
                    ind,
                    metadata_tonic.columns.get_loc('mean_signal')] = scl_epoch[str(
                        ind)]["Signal"].mean()
                metadata_tonic.iloc[
                    ind,
                    metadata_tonic.columns.get_loc('trial_order')] = scl_epoch[str(
                        ind)]['Label'].unique()[0]
                metadata_tonic.iloc[
                    ind, metadata_tonic.columns.get_loc('iv_stim')] = scl_epoch[
                        str(ind)]["Condition"].unique()[0]
            return metadata_tonic

    metadata_tonic = utils.preprocess.combine_metadata_SCL(scl_epoch)
    # 2. eda_level_timecourse ------------------------------------

    def resample_scl2pandas(scl_epoch: dict, tonic_length, sampling_rate:int, desired_sampling_rate: int):
        """
        parameters:
        -----------
        epoch: dict
            epoch derived from `extract_SCL`
        tonic_length: int
            length of full dictionary, extracted from `extract_SCL`
        sampling_rate: int
            original sample rate of dataframe
        desired_sampling_rate: int
            desired downsampled sample rate

        original
        --------
        eda_level_timecourse = pd.DataFrame(
            index=list(range(len(scl_epoch))),
            columns=['time_' + str(col) for col in list(np.arange(tonic_length))])
        try:
            for ind in range(len(scl_epoch)):
                resamp = nk.signal_resample(
                    scl_epoch[str(ind)]['Signal'].to_numpy(),  method='interpolation', sampling_rate=2000, desired_sampling_rate=25)
                eda_level_timecourse.iloc[
                    ind, :] = resamp
        except:
            for ind in range(len(scl_epoch)):
                resamp = nk.signal_resample(
                    scl_epoch[ind]['Signal'].to_numpy(),  method='interpolation', sampling_rate=2000, desired_sampling_rate=25)
                eda_level_timecourse.iloc[
                    ind, :] = resamp
        """
        eda_level_timecourse = pd.DataFrame(
        index=list(range(len(scl_epoch))),
        columns=['time_' + str(col) for col in list(np.arange(tonic_length))])
        try:
            for ind in range(len(scl_epoch)):
                resamp = nk.signal_resample(
                    scl_epoch[str(ind)]['Signal'].to_numpy(),  method='interpolation', sampling_rate=sampling_rate, desired_sampling_rate=desired_sampling_rate)
                eda_level_timecourse.iloc[
                    ind, :] = resamp
        except:
            for ind in range(len(scl_epoch)):
                resamp = nk.signal_resample(
                    scl_epoch[ind]['Signal'].to_numpy(),  method='interpolation', sampling_rate=sampling_rate, desired_sampling_rate=desired_sampling_rate)
                eda_level_timecourse.iloc[
                    ind, :] = resamp
        return eda_level_timecourse

    resample_rate = 25
    tonic_length = np.abs(tonic_epoch_start-tonic_epoch_end) * resample_rate
    eda_level_timecourse = utils.preprocess.resample_scl2pandas(scl_epoch = scl_epoch, tonic_length = tonic_length, sampling_rate = samplingrate, desired_sampling_rate = resample_rate):
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
