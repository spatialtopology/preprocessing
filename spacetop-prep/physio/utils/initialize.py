#!/usr/bin/env python
# encoding: utf-8

import os
from os.path import join
import numpy as np
from pathlib import Path
import re, logging
from . import get_logger, set_logger_level

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

logger = get_logger("initialize")
set_logger_level(logger, os.environ.get("SPACETOP_PHYSIO_LOG_LEVEL", logging.INFO))

def _logger(logger_fname, name):
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

def _extract_bids_num(filename, key):
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
    bids_info_rmext = os.path.splitext(bids_info)[0] 
    bids_num =  int(re.findall('\d+', bids_info_rmext )[0].lstrip('0'))    
    return bids_num

def _extract_bids(filename, key):
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
    bids_info_rmext = os.path.splitext(bids_info)[0] 
    return bids_info_rmext

def _sublist(source_dir, remove_int, slurm_ind, sub_zeropad, stride=10 ):
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
    include_int = list(np.arange(slurm_ind * stride + 1, (slurm_ind + 1) * stride, 1))
    include_list = [f"sub-{x:0{sub_zeropad}d}" for x in include_int]
    sub_list = [x for x in biopac_list if x not in remove_list]
    sub_list = [x for x in sub_list if x in include_list]
    return sub_list

def _subset_meta(metadata_df, sub, ses):
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

def _assign_runnumber(ref_dict, clean_runlist, dict_runs_adjust, main_df, save_dir, run_basename, bids_dict):
    for ind, r in enumerate(clean_runlist): 
        clean_run = list(ref_dict.keys())[ind]
        task_type = ref_dict[clean_run][0]
        run_df = main_df.iloc[dict_runs_adjust['start'][r]:dict_runs_adjust['stop'][r]]
        
        run_basename = f"{bids_dict['sub']}_{bids_dict['ses']}_{bids_dict['task']}_{clean_run}-{task_type}_recording-ppg-eda-trigger_physio.tsv"
        run_dir = os.path.join(save_dir, bids_dict['sub'], bids_dict['ses'])
        Path(run_dir).mkdir(parents=True, exist_ok=True)
        run_df.to_csv(os.path.join(run_dir, run_basename), sep = '\t', index=False)# %%
