#!/usr/bin/env python
"""
Sorts the raw acquisitions files into semi-BIDS format
Note, it is not BIDS yet, because we're not splitting it into runs, yet.

Parameters
------------------
physio_dir: str
    path where physio data lives
acqlist: str
    designate substructure underneath physio_dir
log_savedir: str
    path where error logs should be saved

Returns
------------------
    physio files saved under subject and session id, also named in semi-BIDS format
"""
import os, sys, glob, re, shutil
from pathlib import Path
import traceback
import datetime

pwd = os.getcwd()
main_dir = Path(pwd).parents[0]
sys.path.append(os.path.join(main_dir))
sys.path.insert(0, os.path.join(main_dir))
print(sys.path)

import utils
from utils import preprocess
from utils import initialize

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development"

# %% directories ___________________________________
# NOTE: USER INPUT:
#current_dir = os.getcwd()
#main_dir = Path(current_dir).parents[1]
physio_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/physio'
log_savedir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/log'
logger_fname = os.path.join(
    log_savedir, f"data-physio_step-01-bidsify_{datetime.date.today().isoformat()}.txt")
f = open(logger_fname, "w")
logger = utils.initialize._logger(logger_fname)
acq_list = glob.glob(os.path.join(physio_dir, 'physio01_raw', '**', '*.acq'), recursive = True)
for acq in acq_list:
    try: 
        filename  = os.path.basename(acq)
        sub = utils.initialize._extract_bids(filename, 'sub') # 'sub-0056'
        ses = utils.initialize._extract_bids(filename, 'ses') # 'ses-03'
        task = utils.initialize._extract_bids(filename, 'task')
        logger.info("__________________%s %s %s__________________", sub, ses, task)
        new_dir = os.path.join(physio_dir,'physio02_sort', sub, ses)
        Path(new_dir).mkdir(parents=True,exist_ok=True )
        shutil.copy(acq,new_dir)
    except:
        logger.debug(logger.error)