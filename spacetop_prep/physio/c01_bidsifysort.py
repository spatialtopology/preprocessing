#!/usr/bin/env python
"""
Sorts the raw acquisitions files into semi-BIDS format
NOTE: The output will not be quite BIDS yet,
because we haven't split the physio data into runs, yet.

Parameters
------------------
physio_dir: str
    path where physio data lives
sub_zeropad: int
    how many zeros to pad for BIDS subject id
ses_zeropad: int
    how many zeros to pad for BIDS session id
DEP:acqlist: str
    designate substructure underneath physio_dir
log_savedir: str
    path where error logs should be saved

Returns
------------------
    physio files saved under subject and session id, also named in semi-BIDS format
"""
import argparse
import datetime
import glob
import os
import re
import shutil
import sys
import traceback
from pathlib import Path

from spacetop_prep.physio import utils
from spacetop_prep.physio.utils import initialize, preprocess

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Bethany Hunt"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

def main():

    args = get_args()
    physio_dir = args.raw_physiodir
    sub_zeropad = args.sub_zeropad
    ses_zeropad = args.ses_zeropad
    log_savedir = args.logdir

    # NOTE: create logger file ___________________________________
    logger_fname = os.path.join(
        log_savedir, f"data-physio_step-01-bidsify_{datetime.date.today().isoformat()}.txt")
    f = open(logger_fname, "w")
    logger = utils.initialize.logger(logger_fname, "bidsify")

    # NOTE: glob all acquisition files in physio_dir ___________________________________
    acq_list = glob.glob(os.path.join(physio_dir, 'physio01_raw', '**', '*.acq'), recursive = True)
    for acq in acq_list:
        try:
            filename  = os.path.basename(acq)
            sub_num = utils.initialize.extract_bids_num(filename, 'sub')
            sub = f"sub-{sub_num:0{sub_zeropad}d}" # 'sub-0056'
            ses_num = utils.initialize.extract_bids_num(filename, 'ses')
            ses = f"ses-{ses_num:0{ses_zeropad}d}" # 'ses-03'
            task = utils.initialize.extract_bids(filename, 'task')
            logger.info("__________________%s %s %s__________________", sub, ses, task)

            # NOTE: create new folder -- physio02_sort -- and sort acq files correspondingly
            new_dir = os.path.join(physio_dir,'physio02_sort', sub, ses)
            Path(new_dir).mkdir(parents=True,exist_ok=True )
            if 'ANISO' in acq:
                new_fname = f"{sub}_{ses}_{task}_recording-ppg-eda-trigger_physio.acq"
            else:
                new_fname = f"{sub}_{ses}_{task}_recording-ppg-eda_physio.acq"
            shutil.copy(acq,os.path.join(new_dir,new_fname))
        except:
            logger.debug(logger.error)

def get_args():
    # argument parser _______________________________________________________________________________________
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-physiodir",
                        type=str, help="path where raw physio data lives")
    parser.add_argument("--sub-zeropad",
                        type=str, help="BIDS: number of zeros that are padded for session index")
    parser.add_argument("--ses-zeropad",
                        type=str, help="BIDS: number of zeros that are padded for session index")
    parser.add_argument("--logdir",
                        type=str, help="path where logging outputs will be saved")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
