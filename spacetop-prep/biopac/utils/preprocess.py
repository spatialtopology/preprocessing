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