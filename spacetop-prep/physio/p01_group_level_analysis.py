# assuming that we have all of the run-bids formatted acq.
# load data
# [x] append task info (PVC) from metadata
# [x] move biopac final data into fmriprep: spacetop_data/data/sub/ses/physio
# [x] move behavioral data preprocessed into fmriprep:  spacetop_data/data/sub/ses/beh
# [x] allow to skip broken files
# [x] allow to skip completed files
# baseline correct
# filter signal
# extract mean signals
# export as .csv file
# extract timeseries signal
# export as .csv file
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
"""
# 
# %% libraries _________________________________________________________________________________________
from tkinter import Variable
import neurokit2 as nk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, glob, sys
from pathlib import Path
from os.path import join
import itertools
from statistics import mean
import logging
from datetime import datetime

# cluster = sys.argv[1]
# slurm_ind = sys.argv[2]
pwd = os.getcwd()
main_dir = Path(pwd).parents[1]
cluster = 'local'
if cluster == 'discovery':
    main_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_biopac/'
else:
    main_dir = '/Users/h/Dropbox/projects_dropbox/spacetop_biopac'

sys.path.append(os.path.join(main_dir, 'scripts'))
sys.path.insert(0, os.path.join(main_dir, 'scripts'))
print(sys.path)
import utils
from utils import preprocess
from utils import checkfiles
from utils import initialize
from utils._ttl_extraction import _ttl_extraction

__author__ = "Heejung Jung, Isabel Neumann"
__copyright__ = "Spatial Topology Project"
__credits__ = [
    "Heejung"
]  # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

# TODO:
# operating = sys.argv[1]  # 'local' vs. 'discovery'
# slurm_ind = sys.argv[2] # process participants with increments of 10
# task = sys.argv[3]  # 'task-social' 'task-fractional' 'task-alignvideos'
# run_cutoff = sys.argv[4] # in seconds, e.g. 300
operating = 'local' # 'local' vs. 'discovery'
slurm_ind = 1 # process participants with increments of 10
task = 'task-social'  # 'task-cue' 'task-fractional' 'task-alignvideos'
run_cutoff = 300 # in seconds, e.g. 300
sub_zeropad = 4
run_cutoff = 300
samplingrate = 2000

plt.rcParams['figure.figsize'] = [15, 5]  # Bigger images
plt.rcParams['font.size'] = 14

# %% set parameters
pwd = os.getcwd()
main_dir = pwd
flaglist = []
task = 'task-cue'
cluster='local'
if cluster == 'discovery':
    physio_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social/data/physio/physio01_raw'  #'/Volumes/spacetop/biopac/dartmouth/b04_finalbids/'
    beh_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social/data/beh/d02_preproc-beh'  # '/Volumes/spacetop_projects_social/data/d02_preproc-beh'
    project_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social'
    log_dir = join(project_dir, "scripts", "logcenter")
    
else:
    #physio_dir = '/Volumes/spacetop_projects_social/data/physio/physio01_raw'#'/Volumes/spacetop/biopac/dartmouth/b04_finalbids/'
    physio_dir = '/Volumes/spacetop/biopac/dartmouth/b04_finalbids/task-social'
    beh_dir = '/Volumes/spacetop_projects_social/data/beh/d02_preproc-beh'  # '/Volumes/spacetop_projects_social/data/d02_preproc-beh'
    project_dir = '/Volumes/spacetop_projects_social'
    log_dir = join(project_dir, "scripts", "logcenter")
sub_list = []
#biopac_list = next(os.walk(physio_dir))[1]
remove_int = [1, 2, 3, 4, 5, 6]
sub_list = utils.initialize._sublist(physio_dir, remove_int, slurm_ind, stride=10, sub_zeropad=4)
ses_list = [1, 3, 4]
run_list = [1, 2, 3, 4, 5, 6]
sub_ses = list(itertools.product(sorted(sub_list), ses_list, run_list))
"""
# NOTE: TEST ______________________________________
"""

sub_list = ['sub-0074']; ses_list = [1]; run_list = [1,2,3,4,5,6]
sub_ses = list(itertools.product(sorted(sub_list), ses_list, run_list))
log_dir = '/Users/h/Dropbox/projects_dropbox/spacetop_biopac/sandbox'
physio_dir = '/Users/h/Dropbox/projects_dropbox/spacetop_biopac/sandbox'
"""
# NOTE: TEST ______________________________________
"""
logger_fname = os.path.join(log_dir, f"data-physio_step-04-groupanalysis_{datetime.date.today().isoformat()}.txt")


# set up logger _______________________________________________________________________________________

runmeta = pd.read_csv(
    join(project_dir, "data/spacetop_task-social_run-metadata.csv"))
#TODO: come up with scheme to update logger files
f = open(logger_fname, "w")
logger = utils.initialize._logger(logger_fname)

def _extract_bids(fname):
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
    
    ses = f"ses-{ses_ind:02d}"; run = f"run-{run_ind:02d}"
    logger.info(
        f"\n\n__________________{sub} {ses} {run}__________________")
    physio_flist = utils.checkfiles._glob_physio_bids(physio_dir,sub,ses,task,run)

    try:
        physio_fpath = physio_flist[0]
    except IndexError:
        logger.error(f"\tmissing physio file - {sub} {ses} {run} DOES NOT exist")
        continue
    phasic_fname = os.path.basename(physio_fpath)
    bids_dict = {}
    bids_dict['sub'] = sub = utils.initialize._extract_bids(phasic_fname, 'sub')
    bids_dict['ses'] = ses = utils.initialize._extract_bids(phasic_fname, 'ses')
    bids_dict['task']= task = utils.initialize._extract_bids(phasic_fname, 'task')
    bids_dict['run'] = run = utils.initialize._extract_bids(phasic_fname, 'run')
    logger.info(bids_dict)
    # sub_num, ses_num, run_num, run_type = _extract_bids(
    #     os.path.basename(physio_fpath))
    logger.info(
        f"\n\n__________________{sub} {ses} {run} __________________")
    save_dir = join(project_dir, 'data', 'physio', 'physio02_preproc', sub,
                ses)
    save_dir = join(log_dir, 'data', 'physio', 'physio02_preproc', sub,
                ses)
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
    physio_df = pd.read_csv(physio_fpath)
    

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
    print(f"{sub} {ses} {run} {run_type} ____________________")
    metadata_df = beh_df[[
        'src_subject_id', 'session_id', 'param_task_name', 'param_run_num',
        'param_cue_type', 'param_stimulus_type', 'param_cond_type'
    ]]

# NOTE: merge fixation columns (some files look different) handle slight changes in biopac dataframe
    if 'fixation-01' in physio_df.columns:
        physio_df[
            'fixation'] = physio_df['fixation-01'] + physio_df['fixation-02']

# NOTE: baseline correct _________________________________________________________________________________
    # 1) extract fixations:
    fix_bool = physio_df['fixation'].astype(bool).sum()
    print(
        f"confirming the number of fixation non-szero timepoints: {fix_bool}")
    print(f"this amounts to {fix_bool/samplingrate} seconds")
    # baseline correction method 02: use the fixation period from the entire run
    mask = physio_df['fixation'].astype(bool)
    baseline_method02 = physio_df['Skin Conductance (EDA) - EDA100C-MRI'].loc[
        mask].mean()
    physio_df['EDA_corrected_02fixation'] = physio_df[
        'Skin Conductance (EDA) - EDA100C-MRI'] - baseline_method02

    print(f"baseline using fixation from entire run: {baseline_method02}")

# NOTE: extract epochs ___________________________________________________________________________________
    dict_channel = {'cue': 'cue',
    'expect': 'expectrating',
    'administer': 'stimuli',
    'actual': 'actualrating',
    }
    dict_onset = {}
    for i, (key, value) in enumerate(dict_channel.items()):
        dict_onset[value] = {}
        
        utils.preprocess._binarize_channel(physio_df,
                                        source_col=key,
                                        new_col=value,
                                        threshold=None,
                                        binary_high=5,
                                        binary_low=0)
        dict_onset[value] = utils.preprocess._identify_boundary(physio_df, value)
        logger.info(f"* total number of {value} trials: {len(dict_onset[value]['start'])}")


# NOTE: TTL extraction ___________________________________________________________________________________
    if run_type == 'pain':
        final_df = pd.DataFrame()
        # binarize TTL channels (raise error if channel has no TTL, despite being a pain run)
        metadata_df, plateau_start = _ttl_extraction(
            physio_df = physio_df, 
            dict_beforettl = dict_onset['expectrating'], 
            dict_afterttl = dict_onset['actualrating'], 
            dict_stimuli = dict_onset['stimuli'], 
            samplingrate = samplingrate, 
            metadata_df = metadata_df)

        # create a dictionary for neurokit. this will serve as the events
        event_stimuli = {
            'onset': np.array(plateau_start).astype(pd.Int64Dtype),
            'duration': np.repeat(samplingrate * 5, 12),
            'label': np.array(np.arange(12)),
            'condition': beh_df['param_stimulus_type'].values.tolist()
        }
        # TODO: interim plot to check if TTL matches with signals
        run_physio = physio_df[[
            'EDA_corrected_02fixation', 'Pulse (PPG) - PPG100C', 'ttl'
        ]]
        # run_physio
        # stim_plot = nk.events_plot(event_stimuli, run_physio)
        # TODO: plot and save
    else:
        event_stimuli = {
            'onset': np.array(dict_onset['stimuli']['start']),
            'duration': np.repeat(samplingrate * 5, 12),
            'label': np.array(np.arange(12), dtype='<U21'),
            'condition': beh_df['param_stimulus_type'].values.tolist()
        }
        # TODO: plot the ttl and visulize the alignment
        # interim plot to check if TTL matches with signals
        run_physio = physio_df[[
            'EDA_corrected_02fixation', 'Pulse (PPG) - PPG100C', 'stimuli'
        ]]
        #run_physio
        stim_plot = nk.events_plot(event_stimuli, run_physio)

# NOTE: neurokit analysis :+: HIGHLIGHT :+: filter signal ________________________________________________

    # IF you want to use raw signal
    # eda_signal = nk.signal_sanitize(run_physio["Skin Conductance (EDA) - EDA100C-MRI"])
    # eda_raw_plot = plt.plot(run_df["Skin Conductance (EDA) - EDA100C-MRI"])

# NOTE: PHASIC_____________________________________________________________________________
    amp_min = 0.01
    scr_signal = nk.signal_sanitize(
        physio_df['Skin Conductance (EDA) - EDA100C-MRI'])
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
        print("has NANS in the datafram")
        continue
    scr_phasic = nk.eda_eventrelated(scr_epochs)

# NOTE:  TONIC ________________________________________________________________________________
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
        print("has NANS in the datafram")
        continue

#  NOTE: concatenate dataframes __________________________________________________________________________
    # TODO: create internal function
    # Make it more flexible for selecting which columns to visualize
    if run_type == 'pain':
        bio_df = pd.concat([
            physio_df[[
                'trigger', 'fixation', 'cue', 'expect', 'administer', 'actual',
                'ttl'
            ]], scr_processed
        ],
                        axis=1)
    else:
        bio_df = pd.concat([
            physio_df[[
                'trigger', 'fixation', 'cue', 'expect', 'administer', 'actual',
            ]], scr_processed
        ],
                        axis=1)
    fig_save_dir = join(project_dir, 'data', 'physio', 'qc', sub, ses)
    Path(fig_save_dir).mkdir(parents=True, exist_ok=True)

    fig_savename = f"{sub}_{ses}_{run}-{run_type}_physio-scr-scl.png"
    # processed_fig = nk.events_plot(
    #     event_stimuli,
    #     bio_df[['administer', 'EDA_Tonic', 'EDA_Phasic', 'SCR_Peaks']])
    #plt.show()
    # TODO: plot save
    # Tonic level ______________________________________________________________________________________
    
    # 1. append columns to the begining (trial order, trial type)
    # NOTE: eda_epochs_level -> scl_epoch
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
    # 2. eda_level_timecourse
    eda_level_timecourse = pd.DataFrame(
        index=list(range(len(scl_epoch))),
        columns=['time_' + str(col) for col in list(np.arange(tonic_length))])
    try:
        for ind in range(len(scl_epoch)):
            eda_level_timecourse.iloc[
                ind, :] = scl_epoch[str(ind)]['Signal'].to_numpy().reshape(
                    1, tonic_length
                )  
    except:
        for ind in range(len(scl_epoch)):
            eda_level_timecourse.iloc[
                ind, :] = scl_epoch[ind]['Signal'].to_numpy().reshape(
                    1, tonic_length
                )  


    tonic_df = pd.concat([metadata_df, metadata_tonic], axis=1)
    tonic_timecourse = pd.concat(
        [metadata_df, metadata_tonic, eda_level_timecourse], axis=1)
# NOTE: save tonic data __________________________________________________________________________________

    Path(save_dir).mkdir(parents=True, exist_ok=True)
    tonic_fname = f"{sub}_{ses}_{run}-{run_type}_epochstart--1_epochend-8_physio-scl.csv"
    tonictime_fname = f"{sub}_{ses}_{run}-{run_type}_epochstart--1_epochend-8_physio-scltimecourse.csv"
    tonic_df.to_csv(join(save_dir, tonic_fname))
    tonic_timecourse.to_csv(join(save_dir, tonictime_fname))

# NOTE: save phasic data _________________________________________________________________________________
    metadata_df = metadata_df.reset_index(drop=True)
    scr_phasic = scr_phasic.reset_index(drop=True)
    phasic_meta_df = pd.concat(
        [metadata_df, scr_phasic], axis=1
    )  
    phasic_fname = f"{sub}_{ses}_{run}-{run_type}_epochstart-0_epochend-5_physio-scr.csv"
    phasic_meta_df.to_csv(join(save_dir, phasic_fname))
    print(f"{sub}_{ses}_{run}-{run_type} finished")
    #plt.clf()

    print(f"complete {sub} {ses} {run}")
