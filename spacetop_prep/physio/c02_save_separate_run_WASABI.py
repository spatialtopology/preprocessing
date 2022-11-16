#!/usr/bin/env python
""" 
save_seperate_run_WASABI.py
adjustments for WASABI
Separates acq into runs and saves as bids format. 
This script reads the acquisition file collected straight from our biopac PC

Parameters
------------------
operating: str
    options: 'local' vs. 'discovery'
task: str
    options: 'task-social', 'task-fractional' 'task-alignvideos', 'task-faces', 'task-shortvideos'
run_cutoff: int
    threshold for determining "kosher" runs versus not. 
    for instance, task-social is 398 seconds long. I use the threshold of 300 as a threshold. 
    Anything shorter than that is discarded and not converted into a run
"""

# %% libraries ________________________
import neurokit2 as nk
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
import os
import sys
import shutil
import glob
from pathlib import Path
import json
from itertools import compress
import datetime
from os.path import join
import logging

pwd = os.getcwd()
main_dir = Path(pwd).parents[0]
sys.path.append(os.path.join(main_dir))
sys.path.insert(0, os.path.join(main_dir))
print(sys.path)

from . import utils
from .utils import preprocess
from .utils import initialize

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

# TODO: Users, input this section
operating = sys.argv[1]  # 'local' vs. 'discovery'
slurm_ind = sys.argv[2] # process participants with increments of 10
task = sys.argv[3]  # 'task-social' 'task-fractional' 'task-alignvideos'
run_cutoff = sys.argv[4] # in seconds, e.g. 300
sub_zeropad = 4
run_cutoff = 240
runmeta = runmeta = pd.read_csv('/Users/h/Downloads/WASABI_sample_metadata.txt', sep = ',')

dict_column = {
    'fMRI_ttl':'MRI TR',#'fMRI Trigger - CBLCFMA - Current Feedba',
    'TSA2_ttl':'Medoc TSA2 TTL Out'
}
# spacetop
# dict_column = {
#     'fMRI_ttl':'fMRI Trigger - CBLCFMA - Current Feedba',
#     'TSA2_ttl':'Medoc TSA2 TTL Out'
# }
# %% TODO: TST remove after development
# operating = 'local'  # 'discovery'
# task = 'task-social'
# run_cutoff = 300

if operating == 'discovery':
    spacetop_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social'
    biopac_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/biopac/'
    source_dir = join(biopac_dir, 'dartmouth', 'b02_sorted' )
    save_dir = join(biopac_dir, 'dartmouth', 'b04_finalbids')
elif operating == 'local':
    spacetop_dir = '/Volumes/spacetop_projects_social'
    biopac_dir = '/Volumes/spacetop/biopac'
    source_dir = join(biopac_dir, 'dartmouth', 'b02_sorted' )
    save_dir = join(biopac_dir, 'dartmouth', 'b04_finalbids')

print(spacetop_dir)
print(biopac_dir)
print(save_dir)

# TODO: make runmeta more generic
# runmeta = pd.read_csv(
    # join(spacetop_dir, "data/spacetop_task-social_run-metadata.csv"))

# %%
#TODO: come up with scheme to update logger files
ver = 1
save_dir = '/Users/h/Desktop'
studyname = 'wasabi'
logger_fname = os.path.join(
    save_dir, f"biopac_flaglist_{studyname}_{datetime.date.today().isoformat()}_ver-4.txt")
f = open(logger_fname, "w")
logger = utils.initialize._logger(logger_fname)

# %% 1. glob acquisition files ____________________________________________________________________________
# filename ='/Users/h/Dropbox/projects_dropbox/spacetop_biopac/data/sub-0026/SOCIAL_spacetop_sub-0026_ses-01_task-social_ANISO.acq'
remove_int = [1, 2, 3, 4, 5, 6]
sub_list = utils.initialize._sublist(source_dir, remove_int, slurm_ind, stride=10, sub_zeropad=4)

acq_list = []
for sub in sub_list:
    acq = glob.glob(os.path.join(biopac_dir,  "dartmouth", "b02_sorted", sub, "**", f"*{task}*.acq"),
                     recursive=True)
    acq_list.append(acq)
flat_acq_list = [item for sublist in acq_list  for item in sublist]

# %%
flat_acq_list = ['/Users/h/Downloads/WASABI_sub-00006_ses-15_task-bodymapST1.acq']
for acq in sorted(flat_acq_list):
# NOTE: extract information from filenames _______________________________________________________________
    filename = os.path.basename(acq)
    bids_dict = {}
    bids_dict['sub'] = sub  = utils.initialize._extract_bids(filename, 'sub')
    bids_dict['ses'] = ses  = utils.initialize._extract_bids(filename, 'ses')
    bids_dict['task']= task = utils.initialize._extract_bids(filename, 'task')

# NOTE: open physio dataframe (check if exists) __________________________________________________________
    if os.path.exists(acq):
        main_df, samplingrate = nk.read_acqknowledge(acq)
        logger.info(f"\n\n__________________{sub} {ses} __________________")
        logger.info(f"file exists! -- starting transformation: ")
    else:
        logger.error(f"\tno biopac file exists")
        logger.debug(logger.error)
        logger.error(acq)
        continue
        
# NOTE create an mr_aniso channel for TTL channel _________________________________________________________________________
    try:
        main_df['mr_aniso'] = main_df[dict_column['fMRI_ttl']].rolling(
        window=3).mean()
    except:
        #logger.info(f"\n\n__________________{sub} {ses} __________________")
        logger.error(f"\tno MR trigger channel - this was the early days. re run and use the *trigger channel*")
        logger.error(acq)
        continue
        
    try:
        utils.preprocess._binarize_channel(main_df,
                                        source_col='mr_aniso',
                                        new_col='spike',
                                        threshold=40,
                                        binary_high=5,
                                        binary_low=0)
    except:
        #logger.info(f"\n\n__________________{sub} {ses} __________________")
        logger.error(f"data is empty - this must have been an empty file or saved elsewhere")
        logger.exception("message")
        continue

    dict_spike = utils.preprocess._identify_boundary(main_df, 'spike')
    logger.info(f"number of TRs within experiment: {len(dict_spike['start'])}")
    main_df['bin_spike'] = 0
    main_df.loc[dict_spike['start'], 'bin_spike'] = 5
    # 2)
    try:
        main_df['mr_aniso_boxcar'] = main_df[dict_column['fMRI_ttl']].rolling(
            window=int(samplingrate-100)).mean()
        mid_val = (np.max(main_df['mr_aniso_boxcar']) -
                np.min(main_df['mr_aniso_boxcar'])) / 5
        utils.preprocess._binarize_channel(main_df,
                                        source_col='mr_aniso_boxcar',
                                        new_col='mr_boxcar',
                                        threshold=mid_val,
                                        binary_high=5,
                                        binary_low=0)
    except:
        logger.error(f"ERROR:: binarize RF pulse TTL failure - ALTERNATIVE:: use channel trigger instead")
        logger.debug(logger.error)
        continue

    dict_runs = utils.preprocess._identify_boundary(main_df, 'mr_boxcar')
    logger.info(f"* start_df: {dict_runs['start']}")
    logger.info(f"* stop_df: {dict_runs['stop']}")
    logger.info(f"* total of {len(dict_runs['start'])} runs")

# NOTE: _____________ adjust one TR (remove it!)__________________________________________________________
    sdf = main_df.copy()
    sdf.loc[dict_runs['start'], 'bin_spike'] = 0
    sdf['adjusted_boxcar'] = sdf['bin_spike'].rolling(window=1900).mean()
    mid_val = (np.max(sdf['adjusted_boxcar']) -
               np.min(sdf['adjusted_boxcar'])) / 4
    utils.preprocess._binarize_channel(sdf,
                                       source_col='adjusted_boxcar',
                                       new_col='adjust_run',
                                       threshold=mid_val,
                                       binary_high=5,
                                       binary_low=0)
    dict_runs_adjust = utils.preprocess._identify_boundary(sdf, 'adjust_run')
    logger.info(f"* adjusted start_df: {dict_runs_adjust['start']}")
    logger.info(f"* adjusted stop_df: {dict_runs_adjust['stop']}")

    # 2) identify transitions
    run_list = list(range(len(dict_runs_adjust['start'])))
    try:
        run_bool = ((np.array(dict_runs_adjust['stop'])-np.array(dict_runs_adjust['start']))/samplingrate) > run_cutoff
    except:
        logger.error(f"ERROR:: start and stop datapoints don't match")
        logger.debug(logger.error)
        continue
    clean_runlist = list(compress(run_list, run_bool))
    shorter_than_threshold_length = list(compress(run_list, ~run_bool))


    if len(shorter_than_threshold_length) > 0:
        logger.info(
            f"runs shorter than {run_cutoff} sec: {sub} {ses} {shorter_than_threshold_length} - run number in python order")
    scannote_reference = utils.initialize._subset_meta(runmeta, sub, ses)

    if len(scannote_reference.columns) == len(clean_runlist):
        ref_dict = scannote_reference.to_dict('list')
        run_basename = f"{sub}_{ses}_{task}_CLEAN_RUN-TASKTYLE_recording-ppg-eda_physio.acq"
        utils.initialize._assign_runnumber(ref_dict, clean_runlist, dict_runs_adjust, main_df, save_dir,run_basename,bids_dict)
        # for ind, r in enumerate(clean_runlist): 
        #     clean_run = list(ref_dict.keys())[ind]
        #     task_type = ref_dict[clean_run][0]
        #     run_df = main_df.iloc[dict_runs_adjust['start'][r]:dict_runs_adjust['stop'][r]]
        #     run_basename = f"{sub}_{ses}_{task}_{clean_run}-{task_type}_recording-ppg-eda_physio.acq"
        #     run_dir = os.path.join(save_dir, task, sub, ses)
        #     Path(run_dir).mkdir(parents=True, exist_ok=True)
        #     run_df.to_csv(os.path.join(run_dir, run_basename), index=False)# %%
        logger.info("n__________________ :+: FINISHED :+: __________________")
    else:
        logger.error(f"number of complete runs do not match scan notes")
        logger.debug(logger.error)


# %%
