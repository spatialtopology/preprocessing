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