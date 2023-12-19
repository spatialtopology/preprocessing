# %%
from ..initialize import extract_bids, extract_bids_num, sublist,assign_runnumber
import numpy as np
from pathlib import Path
import os

def test_extract_bids_num():
	assert extract_bids_num("sub-123_ses-01.nii.gz", "sub") == 123
    
def test_extract_bids():
	assert extract_bids("sub-123_ses-01.nii.gz", "sub") == "sub-123"

# %%
def test_sublist():
    source_dir = os.getcwd()
    # make directory
    remove_int = [51,52,63]
    slurm_ind = 4
    stride = 10
    sub_zeropad = 3
    sub_list = []
    for ind in list(np.arange(slurm_ind * stride, (slurm_ind+1) * stride ,1)):
        sub_dir = os.path.join(source_dir,  f"sub-{ind:0{sub_zeropad}d}")
        Path(sub_dir).mkdir(parents=True,exist_ok=True )
    print(sublist(source_dir, remove_int, slurm_ind, sub_zeropad, stride=10 ))
    assert sublist(source_dir, remove_int, slurm_ind, sub_zeropad, stride=10 ) == ['sub-053','sub-054','sub-055','sub-056','sub-057', 'sub-058','sub-059']

def test_subset_meta():
    # TODO: add mock pandas .csv

def test_assign_runnumber():
    clean_runlist = [1,4,5]
    assign_runnumber(ref_dict, clean_runlist, dict_runs_adjust, main_df, save_dir, run_basename, bids_dict)
    # for numpy it would be smth like
    #import numpy as npsd
    #assert np.all(binarize(range(5), 2) == np.array([0, 0, 0, 1, 1]))

# %%
