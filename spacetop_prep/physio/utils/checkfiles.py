#!/usr/bin/env python
# encoding: utf-8

import os
import glob
from os.path import join
import re, logging
# from . import get_logger, set_logger_level

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

# logger = get_logger("checkfiles")
logger = logging.getLogger("physio.checkfiles")
def glob_physio_bids(biopac_dir, sub, ses, task, run):
    """
    * Globs the BIDS-formmated physio files. 
    * Filenames must explicitly follow the structure of 
    "{sub}_{ses}_{task}_*{run}*_recording-ppg-eda_physio.acq"
    * Filenames should explicitly follow the BIDS folder structure of "{physio_dir}/{sub}/{ses}

    Parameters
    ----------
    biopac_dir: str
        top directory where the BIDS-formmated physio file lives.
    sub: str
        subject id, e.g. "sub-0016"
    ses: str
        session id, e.g. "ses-01"
    task: str 
        threshold for binarizing values within pandas column
    run: str 
        minimum and maximum value for binarizing signal
        e.g. binary_high = 5, binary_low = 0 
             or binary_high = 1, binary_low = 0

    Returns
    -------
    a globbed file list - in theory, only one item should exist in the list
    """

    physio_flist = glob.glob(
    join(
        biopac_dir, '**', sub, ses,
        f"{sub}_{ses}_{task}_*{run}*_recording-ppg-eda*_physio.tsv"
    ), recursive= True)
    return physio_flist

def preproc_scr(save_dir, phasic_fname):

    """
    if file does not exist, run code TODO: figure out how to continue
    if file does exist, exit code 
    """
    if not os.path.exists(glob.glob(join(save_dir, phasic_fname))[0]):
        logger.info("file doesn't exist - carry on!")
    else: 
        logger.error("file exists - abort")
        logger.debug(logger.error)
