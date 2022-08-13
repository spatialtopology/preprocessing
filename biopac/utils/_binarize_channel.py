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

    if not bool(threshold):
        threshold = (np.max(df[source_col]) - np.min(df[source_col]))/2

    df.loc[df[source_col] > threshold, new_col] = binary_high
    df.loc[df[source_col] <= threshold, new_col] = binary_low
