import itertools
import json
import logging
import os
from pathlib import Path

import neurokit2 as nk
import numpy as np
import pandas as pd

# from . import get_logger, set_logger_level

# def get_logger(name=None):
#     """Return a logger to use"""
#     return logging.getLogger("physio" + (".%s" % name if name else ""))

# def set_logger_level(logger, level):
#     if isinstance(level, int):
#         pass
#     elif level.isnumeric():
#         level = int(level)
#     elif level.isalpha():
#         level = getattr(logging, level)
#     else:
#         logger.warning("Do not know how to treat loglevel %s" % level)
#         return
#     logger.setLevel(level)

logger = logging.getLogger("physio.preprocess")

def binarize_channel(df, source_col, new_col, threshold, binary_high, binary_low):
    """
    Function binarizes signals from biopac digital channels.
    If an explicit threshold value is provided, the signals are binarized based on this input.
    If not, the implicit threshold will default to the midpoint of the min/max values of the channel.

    Parameters
    ----------
    df: pandas dataframe
        acquisition file loaded into pandas using nk.read_acqknowledge.
    source_col: str
        column name of df that contains raw signal
    new_col: str
        new column name for saving binarized source_col values. (prevent from overwriting original data)
    threshold: int
        threshold for binarizing values within pandas column
    binary_high, binary_low: int
        minimum and maximum value for binarizing signal
        e.g. binary_high = 5, binary_low = 0
             or binary_high = 1, binary_low = 0

    Returns
    -------
    dataframe with new_col, which consists of binary values.

    For example:
        mid_val = (np.max(run_df['expect']) - np.min(run_df['expect']))/2
        run_df.loc[run_df['expect'] > mid_val, 'expect_rating'] = 5
        run_df.loc[run_df['expect'] <= mid_val, 'expect_rating'] = 0
    """

    import numpy as np

    if not bool(threshold):
        threshold = (np.max(df[source_col]) - np.min(df[source_col]))/2

    df.loc[df[source_col] > threshold, new_col] = binary_high
    df.loc[df[source_col] <= threshold, new_col] = binary_low


def _extract_runs(df, dict, run_num):
    """
    based on identified run transitions, extract each run

    Parameters
    ----------
    df: pandas dataframe
        acquisition file loaded into pandas using nk.read_acqknowledge.
    dict: dict
        dictionary that contains two keys:
        1) {EVENT_NAME}_start = list(dict_transition.keys())[0]
        2) {EVENT_NAME}_stop = list(dict_transition.keys())[1]
        each values are stored as lists of index numbers.
        For example,
            {'experiment_start': [43850, 890568, 1765932, 2603584, 3458812, 4302610],
            'experiment_stop': [841528, 1688195, 2563573, 3401638, 4256488, 5100278]}
    run_num: int
        run number for extracting run chunks out of acquisition file

    Returns
    -------
    dataframe, subset with only specific run signals.

    """
    run_subset = df[dict[list(dict.keys())[0]][run_num-1]: dict[list(dict.keys())[1]][run_num-1]]
    run_df = run_subset.reset_index()
    return run_df

def identify_boundary(df, binary_col):
    """
    Function used to extract onsets of the beginning of an event ("start") and end of an event ("stop").
    The function identifies transitions of events and saves both "start" and "stop" of an event.

    Parameters
    ----------
    df: pandas dataframe
        acquisition file loaded into pandas using nk.read_acqknowledge.
    binary_col: str
        column name of df that contains binary_col
    event_name: str
        dictionary key value name. Make sure to provide a unique event name across events.

    Returns
    -------
    dict: dictionary
        contains onsets of the beginning of an event ("start") and end of an event ("stop")
    """
    dict = {}
    start = df[df[binary_col] > df[binary_col].shift(1)].index.values.tolist()
    stop = df[df[binary_col] < df[binary_col].shift(1)].index.values.tolist()
    dict = {'start': start,
            'stop': stop}
    return dict

def _binarize_trigger_mri(df, dict_column, samplingrate, run_cutoff):
    """
    Function used to turn `trigger_mri` channel into a boxcar.
    The function identifies TRs within a (1/samplingrate * 3) second period, transforms them into a continuous signal of boxcars.
    Using the outputs of this function, we can identify run transitions

    Parameters
    ----------
    run_list: list
        full list of identified run transitions
    clean_runlist: list
        partial list of identified runs that are longer than the run cutoff
    shorter_than_threshold_length: list
        partial list of identified runs that are shorter than the run cutoff
    """
    # TODO: need help from Yarik
    try:
        trigger_mri = [i for i in dict_column if dict_column[i]=="trigger_mri"][0]
        df['trigger_mri_win_3'] = df[trigger_mri].rolling(
        window=3).mean()
    except:
        logger.error("no MR trigger channel - this was the early days. re run and use the *trigger channel*")
        # logger.error(acq)
        # continue
    # TST: files without trigger keyword in the acq files should raise exception
    try:
        binarize_channel(df,
                                        source_col='trigger_mri_win_3',
                                        new_col='trigger_mri_win_3',
                                        threshold=40,
                                        binary_high=5,
                                        binary_low=0)
    except:
        logger.error(f"data is empty - this must have been an empty file or saved elsewhere")
        # continue
        raise

    dict_spike = identify_boundary(df, 'trigger_mri_win_3')
    logger.info("number of spikes within experiment: %d", len(dict_spike['start']))
    df['bin_spike'] = 0
    df.loc[dict_spike['start'], 'bin_spike'] = 5

    # NOTE: 5. create an trigger_mri_win_3 channel for MRI RF pulse channel ________________________________________________
    try:
        df['trigger_mri_win_samprate'] = df[trigger_mri].rolling(
            window=int(samplingrate-100)).mean()
        mid_val = (np.max(df['trigger_mri_win_samprate']) -
                np.min(df['trigger_mri_win_samprate'])) / 5
        binarize_channel(df,
                                        source_col='trigger_mri_win_samprate',
                                        new_col='mr_boxcar',
                                        threshold=mid_val,
                                        binary_high=5,
                                        binary_low=0)
    except:
        logger.error(f"ERROR:: binarize RF pulse TTL failure - ALTERNATIVE:: use channel trigger instead")
        logger.debug(logger.error)
        raise
        # continue
    dict_runs = identify_boundary(df, 'mr_boxcar')
    logger.info("* start_df: %s", dict_runs['start'])
    logger.info("* stop_df: %s", dict_runs['stop'])
    logger.info("* total of %d runs", len(dict_runs['start']))

    # NOTE: 6. adjust one TR (remove it!)_________________________________________________________________________
    sdf = df.copy()
    sdf.loc[dict_runs['start'], 'bin_spike'] = 0
    sdf['adjusted_boxcar'] = sdf['bin_spike'].rolling(window=int(samplingrate-100)).mean()
    mid_val = (np.max(sdf['adjusted_boxcar']) -
               np.min(sdf['adjusted_boxcar'])) / 4
    binarize_channel(sdf,
                                       source_col='adjusted_boxcar',
                                       new_col='adjust_run',
                                       threshold=mid_val,
                                       binary_high=5,
                                       binary_low=0)
    dict_runs_adjust = identify_boundary(sdf, 'adjust_run')
    logger.info("* adjusted start_df: %s", dict_runs_adjust['start'])
    logger.info("* adjusted stop_df: %s", dict_runs_adjust['stop'])

    # NOTE: 7. identify run transitions ___________________________________________________________________________
    run_list = list(range(len(dict_runs_adjust['start'])))
    try:
        run_bool = ((np.array(dict_runs_adjust['stop'])-np.array(dict_runs_adjust['start']))/samplingrate) > run_cutoff
    except:
        logger.error("start and stop datapoints don't match")
        logger.debug(logger.error)
        raise
        # continue
    clean_runlist = list(itertools.compress(run_list, run_bool))
    shorter_than_threshold_length = list(itertools.compress(run_list, ~run_bool))

    return run_list, clean_runlist, shorter_than_threshold_length

def identify_fixation_sec(df: pd.DataFrame, baseline_col: str, samplingrate: int):
    """
    identify how many timepointts there are for column to baseline correct

    parameters
    ----------
    df
    baseline_col
    samplingrate
    """
    fix_bool = df[baseline_col].astype(bool).sum()
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
    """
    # dict_savedir = join(output_savedir, 'physio01_SCL', sub, ses)
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    # dict_fname = f"{sub}_{ses}_{run}_runtype-{run_type}_onset.json"
    out_file = open(os.path.join(save_dir,save_fname), "w+")
    json.dump(dict_onset, out_file)


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
    # TODO: work on plot function
    # plot_SCRprocessed(df, plt_col, scr_processed, plt_savedir)
    try:
        scr_epochs = nk.epochs_create(scr_processed,
                                        event_stimuli,
                                        sampling_rate=samplingrate,
                                        epochs_start=epochs_start,
                                        epochs_end=epochs_end,
                                        baseline_correction=baseline_correction)  #
    except:
        logger.info("has NANS in the dataframe")

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

def extract_SCL(df: pd.DataFrame, eda_col, event_dict, samplingrate, SCL_start, SCL_end, baseline_truefalse):
    """
    1) sanitize
    2) filter
    3) detrend
    4) decompose
    5) extract events

    parameters:
    ----------
    df: pd.DataFrame
    eda_col: str
        eda column to sanize
    event_dict: dict



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
                                        baseline_correction=baseline_truefalse)
        scl_raw = nk.epochs_create(scl_detrend,
                                event_dict,
                                sampling_rate=samplingrate,
                                epochs_start=SCL_start,
                                epochs_end=SCL_end,
                                baseline_correction=baseline_truefalse)
        return tonic_length, scl_raw, scl_epoch
    except:
        logger.info("has NANS in the dataframe")



def combine_metadata_SCL(scl_epoch, metadata_df, total_trial = 12):
    """
    parameters
    ----------
    original code
    -------------
    metadata_SCL = pd.DataFrame(
    index=list(range(len(scl_epoch))),
    columns=['trial_order', 'iv_stim', 'mean_signal'])
    try:
        for ind in range(len(scl_epoch)):
            metadata_SCL.iloc[
                ind, metadata_SCL.columns.
                get_loc('mean_signal')] = scl_epoch[ind]["Signal"].mean()
            metadata_SCL.iloc[
                ind, metadata_SCL.columns.
                get_loc('trial_order')] = scl_epoch[ind]['Label'].unique()[0]
            metadata_SCL.iloc[
                ind, metadata_SCL.columns.
                get_loc('iv_stim')] = scl_epoch[ind]["Condition"].unique()[0]
    except:
        for ind in range(len(scl_epoch)):
            metadata_SCL.iloc[
                ind,
                metadata_SCL.columns.get_loc('mean_signal')] = scl_epoch[str(
                    ind)]["Signal"].mean()
            metadata_SCL.iloc[
                ind,
                metadata_SCL.columns.get_loc('trial_order')] = scl_epoch[str(
                    ind)]['Label'].unique()[0]
            metadata_SCL.iloc[
                ind, metadata_SCL.columns.get_loc('iv_stim')] = scl_epoch[
                    str(ind)]["Condition"].unique()[0]
    ---
    """
    metadata_SCL = pd.DataFrame(
    index=list(range(total_trial)),
    columns=['trial_order', 'iv_stim', 'mean_signal'])

    try:
        for ind in range(len(scl_epoch)):
            dropped_index = metadata_df.reset_index().loc[ind,'trial_num']-1
            metadata_SCL.iloc[
                dropped_index, metadata_SCL.columns.
                get_loc('mean_signal')] = scl_epoch[ind]["Signal"].mean()
            metadata_SCL.iloc[
                dropped_index, metadata_SCL.columns.
                get_loc('trial_order')] = metadata_df.reset_index().loc[ind, 'trial_num'] #metadata_df.loc[ind, 'trial_num'] #scl_epoch[ind]['Label'].unique()[0]
            metadata_SCL.iloc[
                dropped_index, metadata_SCL.columns.
                get_loc('iv_stim')] = scl_epoch[ind]["Condition"].unique()[0]
        # return metadata_SCL

    except:
        for ind in range(len(scl_epoch)):
            dropped_index = metadata_df.reset_index().loc[ind,'trial_num']-1
            metadata_SCL.iloc[
                dropped_index,
                metadata_SCL.columns.get_loc('mean_signal')] = scl_epoch[str(
                    ind)]["Signal"].mean()
            metadata_SCL.iloc[
                dropped_index,
                metadata_SCL.columns.get_loc('trial_order')] =metadata_df.reset_index().loc[ind, 'trial_num']
            metadata_SCL.iloc[
                dropped_index, metadata_SCL.columns.get_loc('iv_stim')] = scl_epoch[
                    str(ind)]["Condition"].unique()[0]
    return metadata_SCL

def combine_metadata_SCR(scr_phasic, metadata_df, total_trial = 12):
    """
    parameters
    ----------

    """
    metadata_SCR = pd.DataFrame(
    index=list(range(total_trial)),
    columns=scr_phasic.columns)

    for ind in range(len(scr_phasic)):
        dropped_index = metadata_df.reset_index().loc[ind,'trial_num']-1
        metadata_SCR.iloc[dropped_index, :] = scr_phasic.iloc[ind,:]
                # eda_level_timecourse.iloc[
                # ind, :] = resamp

    return metadata_SCR


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
        scl_epoch_dropNA = scl_epoch.copy()
        for ind in range(len(scl_epoch)):
            scl_epoch_dropNA = scl_epoch[str(ind)]['Signal'].ffill()
            scl_epoch_reset = scl_epoch_dropNA.reset_index()
            resamp = nk.signal_resample(
                scl_epoch_reset[str(ind)]['Signal'].to_numpy(),  method='interpolation', sampling_rate=sampling_rate, desired_sampling_rate=desired_sampling_rate)
            eda_level_timecourse.iloc[
                ind, :] = resamp
        logger.info("[ind] string")
    except:
        scl_epoch_dropNA = scl_epoch.copy()
        for ind in range(len(scl_epoch)):
            scl_epoch_dropNA = scl_epoch[ind]['Signal'].ffill()
            # scl_epoch_reset = scl_epoch_dropNA.reset_index()
            resamp = nk.signal_resample(
                scl_epoch_reset[ind]['Signal'].to_numpy(),  method='interpolation', sampling_rate=sampling_rate, desired_sampling_rate=desired_sampling_rate)
            eda_level_timecourse.iloc[
                ind, :] = resamp
        logger.info("[ind] integer")
    return eda_level_timecourse

def resample_scl2pandas_ver2(scl_output: dict, metadata_df, total_trial, tonic_length, sampling_rate:int, desired_sampling_rate: int):
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
    index=list(range(total_trial)),
    columns=['time_' + str(col) for col in list(np.arange(tonic_length))])

    try:
        for ind in range(len(scl_output)):
            dropped_index = metadata_df.reset_index().loc[ind,'trial_num']-1
            scl_epoch_dropNA = scl_output[str(ind)]['Signal'].ffill()
            resamp = nk.signal_resample(
                scl_epoch_dropNA.to_numpy(),  method='interpolation', sampling_rate=sampling_rate, desired_sampling_rate=desired_sampling_rate)
            eda_level_timecourse.iloc[
                dropped_index, :] = resamp
        logger.info("[ind] string")
    except:
        for ind in range(len(scl_output)):
            dropped_index = metadata_df.reset_index().loc[ind,'trial_num']-1
            scl_epoch_dropNA = scl_output[ind]['Signal'].ffill()
            resamp = nk.signal_resample(
                scl_epoch_dropNA.to_numpy(),  method='interpolation', sampling_rate=sampling_rate, desired_sampling_rate=desired_sampling_rate)
            eda_level_timecourse.iloc[
                dropped_index, :] = resamp
        logger.info("[ind] integer")
    return eda_level_timecourse

def substitute_beh_NA(nan_index, metadata_df, beh_col):
    """
    If there was a pain trial that wasn't triggered,
    substitute behavioral rating and fill it with NaNs
    """
    nan_ind = nan_index
    metadata = metadata_df.copy()
    for nan_ind in nan_index:
        for col in beh_col:
            metadata.loc[nan_ind, metadata_df.columns.str.contains(col)] = np.nan
    return metadata
