import neurokit2 as nk
import pandas as pd


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
