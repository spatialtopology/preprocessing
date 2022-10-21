import pandas as pd
import numpy as np
import logging
import os
import utils
import itertools
from . import get_logger, set_logger_level

logger = get_logger("preprocess")
set_logger_level(logger, os.environ.get("SPACETOP_PHYSIO_LOG_LEVEL", logging.INFO))

def _binarize_channel(df, source_col, new_col, threshold, binary_high, binary_low):
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
        new column name for saving binarized source_col values. (prevent from overwritting original data)
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

def _identify_boundary(df, binary_col):
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
        utils.preprocess._binarize_channel(df,
                                        source_col='trigger_mri_win_3',
                                        new_col='trigger_mri_win_3',
                                        threshold=40,
                                        binary_high=5,
                                        binary_low=0)
    except:
        logger.error(f"data is empty - this must have been an empty file or saved elsewhere")
        # continue
        raise

    dict_spike = utils.preprocess._identify_boundary(df, 'trigger_mri_win_3')
    logger.info("number of spikes within experiment: %d", len(dict_spike['start']))
    df['bin_spike'] = 0
    df.loc[dict_spike['start'], 'bin_spike'] = 5
    
    # NOTE: 5. create an trigger_mri_win_3 channel for MRI RF pulse channel ________________________________________________
    try:
        df['trigger_mri_win_samprate'] = df[trigger_mri].rolling(
            window=int(samplingrate-100)).mean()
        mid_val = (np.max(df['trigger_mri_win_samprate']) -
                np.min(df['trigger_mri_win_samprate'])) / 5
        utils.preprocess._binarize_channel(df,
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
    dict_runs = utils.preprocess._identify_boundary(df, 'mr_boxcar')
    logger.info("* start_df: %s", dict_runs['start'])
    logger.info("* stop_df: %s", dict_runs['stop'])
    logger.info("* total of %d runs", len(dict_runs['start']))

    # NOTE: 6. adjust one TR (remove it!)_________________________________________________________________________
    sdf = df.copy()
    sdf.loc[dict_runs['start'], 'bin_spike'] = 0
    sdf['adjusted_boxcar'] = sdf['bin_spike'].rolling(window=int(samplingrate-100)).mean()
    mid_val = (np.max(sdf['adjusted_boxcar']) -
               np.min(sdf['adjusted_boxcar'])) / 4
    utils.preprocess._binarize_channel(sdf,
                                       source_col='adjusted_boxcar',
                                       new_col='adjust_run',
                                       threshold=mid_val,
                                       binary_high=5,
                                       binary_low=0)
    dict_runs_adjust = utils.preprocess._identify_boundary(sdf, 'adjust_run')
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