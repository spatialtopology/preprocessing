#!/usr/bin/env python
# encoding: utf-8
# %%
import argparse
import logging
import os
import re
from os.path import join
from pathlib import Path

import numpy as np

# from . import get_logger, set_logger_level

# %%
__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Yarik"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

logger = logging.getLogger("physio.initialize")
# logger = get_logger("initialize")

def logger(logger_fname, name):
    import logging
    formatter = logging.Formatter("%(levelname)s - %(funcName)s:%(lineno)d - %(message)s")
    handler = logging.FileHandler(logger_fname)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)
    logging.getLogger().addHandler(ch)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

def extract_bids_num(filename: str, key: str) -> int:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extention, code will remove it.

    Parameters
    ----------
    filename: str
        acquisition filename
    key: str
        BIDS prefix, such as 'sub', 'ses', 'task'
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    # bids_info_rmext = os.path.splitext(bids_info)[0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    bids_num =  int(re.findall(r'\d+', bids_info_rmext[0] )[0].lstrip('0'))
    return bids_num

def extract_bids(filename: str, key: str) -> str:
    """
    Extracts BIDS information based on input "key" prefix.
    If filename includes an extention, code will remove it.

    Parameters
    ----------
    filename: str
        acquisition filename
    key: str
        BIDS prefix, such as 'sub', 'ses', 'task'
    """
    bids_info = [match for match in filename.split('_') if key in match][0]
    bids_info_rmext = bids_info.split(os.extsep, 1)
    print(bids_info_rmext)
    # 'filename.ext1.ext2'.split(os.extsep, 1)
    # bids_info_rmext = os.path.splitext(bids_info)[0]
    return bids_info_rmext[0]

def sublist(source_dir:str, remove_int:list, slurm_id:int, sub_zeropad:int, stride:int ) -> list:
    """
    Create a subject list based on exclusion criterion.
    Also, restricts the job to number of batches, based on slurm_ind and stride

    Parameters
    ----------
    source_dir: str
        path where the physio data lives
    remove_int: list
        list of numbers (subjuct numbers) to remove
        e.g. [1, 2, 3, 120]
    slurm_ind: int
        number to indicate index of when batch begins
        if running code via SLURM, slurm_ind is a parameter from slurm array
    stride: int
        default 10
        based on slurm_ind, we're going to run "stride" number of participants at once
    sub_zeropad: int
        number of zeropadding that you add to your subject id
        e.g. sub-0004 > sub_zeropad = 4
             sub-000128 > sub_zeropad = 6

    Returns
    -------
    sub_list: list
        a list of subject ids to operate on
    """
    biopac_list = next(os.walk(join(source_dir)))[1]
    remove_list = [f"sub-{x:0{sub_zeropad}d}" for x in remove_int]
    include_int = list(np.arange(slurm_id * stride + 1, (slurm_id + 1) * stride, 1))
    include_list = [f"sub-{x:0{sub_zeropad}d}" for x in include_int]
    sub_list = [x for x in biopac_list if x not in remove_list]
    sub_list = [x for x in sub_list if x in include_list]
    return sorted(sub_list)

def subset_meta(metadata_df, sub:str, ses:str) -> list:
    """
    Selects a subset of metadata pandas, based on sub and ses key

    Parameters
    ----------
    metadata_df: pandas dataframe
        data frame from metadata.csv
    sub: str
        BIDS-formatted subject id, MUST match the sub field in metadata_df and .acq file, e.g. 'sub-0001'
    ses: str
        BIDS-formatted session id, e.g. 'ses-02'

    Returns
    -------
    scannote_reference: list
        a list of subject ids to operate on
    """
    scannote_reference = metadata_df.loc[(metadata_df['sub'] == sub)& (metadata_df['ses'] == ses)]
    scannote_na = scannote_reference.dropna(axis = 1).copy() # NOTE: if a run was aborted, keep as NA - we will drop this "run" column
    scannote_runcol = scannote_na.drop(['sub', 'ses'], axis=1).copy()
    return scannote_runcol

def assign_runnumber(ref_dict, clean_runlist, dict_runs_adjust, main_df, save_dir, run_basename, bids_dict):
    for ind, r in enumerate(clean_runlist):
        clean_run = list(ref_dict.keys())[ind]
        task_type = ref_dict[clean_run][0]
        run_df = main_df.iloc[dict_runs_adjust['start'][r]:dict_runs_adjust['stop'][r]]

        run_basename = f"{bids_dict['sub']}_{bids_dict['ses']}_{bids_dict['task']}_{clean_run}-{task_type}_recording-ppg-eda-trigger_physio.tsv"
        run_dir = os.path.join(save_dir, bids_dict['sub'], bids_dict['ses'])
        Path(run_dir).mkdir(parents=True, exist_ok=True)
        run_df.to_csv(os.path.join(run_dir, run_basename), sep = '\t', index=False)# %%

def glob_corresponding_beh(file2check: str):
    """glob specific string and return one behavioral file
    TODO: raise error if not existt"""
    file2check = glob.glob(
        join(beh_dir, sub, ses,
                f"{sub}_{ses}_task-social_{run}*_beh.csv"))
    beh_fname = file2check[0]
    return beh_fname

def check_beh_exist(file2check: str):
    try:
        beh_fname = glob_corresponding_beh(file2check)
        return beh_fname
    except IndexError:
        logger.error(
            "missing behavioral file: {sub} {ses} {run} DOES NOT exist")

def check_run_type(beh_fname: str):
    run_type = ([match for match in os.path.basename(
        beh_fname).split('_') if "run" in match][0]).split('-')[2]
    return run_type

def argument_p01():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-physiodir",
                        type=str, help="path where BIDS converted physio data lives")
    parser.add_argument("--input-behdir",
                        type=str, help="path where BIDS converted behavioral data lives")
    parser.add_argument("--output-logdir",
                        type=str, help="path where logs will be saved - essential for re-running failed participants")
    parser.add_argument("--output-savedir",
                        type=str, help="path where transformed physio data will be saved")
    parser.add_argument("--metadata",
                        type=str, help=".csv filepath to metadata file of run information (complete/runtype etc)")
    parser.add_argument("--dictchannel",
                        type=str, help=".json file for changing physio data channel names | key:value == old_channel_name:new_channel_name")
    parser.add_argument("-sid", "--slurm-id", type=int,
                        help="specify slurm array id")
    parser.add_argument("--stride", type=int,
                        help="how many participants to batch per jobarray")
    parser.add_argument("-z", "--zeropad",
                        type=int, help="how many zeros are padded for BIDS subject id")
    parser.add_argument("-t", "--task",
                        type=str, help="specify task name (e.g. task-alignvideos)")
    parser.add_argument("-sr", "--samplingrate", type=int,
                        help="sampling rate of acquisition file")
    parser.add_argument("--tonic-epochstart", type=int,
                        help="beginning of epoch")
    parser.add_argument("--tonic-epochend", type=int,
                        help="end of epoch")
    parser.add_argument("--ttl-index", type=int,
                        help="index of which TTL to use")
    args = parser.parse_args()

    physio_dir = args.input_physiodir
    beh_dir = args.input_behdir
    log_dir = args.output_logdir
    output_savedir = args.output_savedir
    metadata = args.metadata
    dictchannel_json = args.dictchannel
    slurm_id = args.slurm_id  # e.g. 1, 2
    stride = args.stride  # e.g. 5, 10, 20, 1000
    zeropad = args.zeropad  # sub-0016 -> 4
    task = args.task  # e.g. 'task-social' 'task-fractional' 'task-alignvideos'
    samplingrate = args.samplingrate  # e.g. 2000
    tonic_epoch_start = args.tonic_epochstart
    tonic_epoch_end = args.tonic_epochend
    ttl_index = args.ttl_index

    return physio_dir,beh_dir,log_dir,output_savedir,metadata, \
    dictchannel_json,slurm_id,stride,zeropad,task,samplingrate, \
    tonic_epoch_start,tonic_epoch_end,ttl_index
