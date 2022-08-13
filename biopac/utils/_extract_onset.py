def _extract_onset(df, binary_col, event_name):
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
    start = df[df[binary_col] > df[binary_col].shift(1)]
    stop = df[df[binary_col] < df[binary_col].shift(1)]
    key_start = str(event_name) + '_start'
    key_stop = str(event_name) + '_stop'
    dict = {key_start: start,
            key_stop: stop}
    return dict