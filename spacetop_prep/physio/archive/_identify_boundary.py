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
    key_start = '_start'
    key_stop = '_stop'
    dict = {key_start: start,
            key_stop: stop}
    return dict