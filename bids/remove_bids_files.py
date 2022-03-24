#!/usr/bin/env python3
"""
the purpose of this script is to automate the "removing-dup" process in datalad. 
Once a duplicate file is confirmed and removed, we need to update 3 sources
- Datalad remove and save duplicate files
- Update file in *.scans.tsv
- Update in IntendedFor field in the fieldmap .json files
This script is to update the IntendedFor field in the fieldmap jsons
"""
from heudiconv.utils import load_json
from heudiconv.utils import save_json
import os, time, sys, glob
from os.path import join
import json

# example file dir
# /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth/sub-0085/ses-01/func/sub-0085_ses-01_task-alignvideo_acq-mb8_run-01_bold__dup-01.nii.gz'
# {main_dir}/{sub}/{ses}/func

# 1. get list of dup names _____________________________________________________________
    # TODO: remove all 4 types of files - See if you can remove and datalad save within this script.
    # 1) remove bold__dup-01.json
    # 2) remove bold__dup-01.nii.gz
    # 3) remove sbref__dup-01.json
    # 4) remove sbref__dup-01.nii.gz
main_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth'
save_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/scripts/spacetop_log'
dup_pattern = 'sub-*/ses-*/func/sub-*_ses-*_task-*_acq-mb8_run-*_bold__dup*.nii.gz'

dup_glob = glob.glob(join(main_dir, dup_pattern))
flaglist = []
flaglist.append(f"This file keeps track of dup file and fieldmap mismatches.\nTwo erroneous cases:\n 1) IntendedFor field does not exist from the get go [IntendedFor X] \n 2) IntendedFor field exists. However, Duplicate file does not exist within this key [IntendedFor O; Dup X]")
for ind, dup_fpath in enumerate(dup_glob):
    
    dup_fname  = os.path.basename(dup_fpath)
    sub = [match for match in dup_fname.split('_') if "sub" in match][0] 
    ses = [match for match in dup_fname.split('_') if "ses" in match][0] 
    run = [match for match in dup_fname.split('_') if "run" in match][0] 
    task = [match for match in dup_fname.split('_') if "task" in match][0] 
# 2. open fieldmap .json with corresponding .dup files _____________________________________________________________
    fmap_glob = glob.glob(join(main_dir, f'{sub}/{ses}/fmap/{sub}_{ses}_acq-mb8_dir-*_epi.json'))
    for fmap_ind, fmap_fname in enumerate(fmap_glob):
        f = load_json(fmap_fname)
        # 2-1. check if "IntendedFor" field exists within json
        key_field = [i for i, s in enumerate(f.keys()) if 'IntendedFor' in s]
        if key_field:
            copy_list = f['IntendedFor']
            print(copy_list)
            # 2-2. find "IntendedFor" field and if dup_fname exists, pop item
            dup_index = [i for i, s in enumerate(copy_list) if dup_fname in s]
            if dup_index:
                copy_list.pop(dup_index[0])
                f['IntendedFor'] = copy_list
                print(f"removed {dup_fname} from list")

                save_json(fmap_fname, f)
            else:
                flag_msg1 = f"Intended For field exists - dup filename does not exist : {dup_fname}"
                flaglist.append(flag_msg1)
            
        elif not key_field:
            flag_msg2 = f"IntendedFor field does not exist - {fmap_fname}"
            print(flag_msg2)
            flaglist.append(flag_msg2)

# 3. save filenames with missing intendedfor fields or missing dup filenames __________________________________________
txt_filename = os.path.join(save_dir, 'dup_flaglist.txt')
with open(txt_filename, 'w') as f:
    f.write(json.dumps(flaglist))




# TODO: delete later. clean up anything below __________________________________________
# 3-3. if the file is at the end of the list, deleted 
# if dup_index[0] == len(copy_list)-1:
#     copy_list.pop(-1)
#     print(f"removed {dup_fname} from list")
#     f['IntendedFor'] = copy_list
# 3-4. if the file is in the middle of the list, simply delete
# elif dup_index[0] < len(copy_list)-1:

# conda activate spacetop_env (within shell script)
# /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth/sub-0009/ses-01/fmap/sub-0009_ses-01_acq-mb8_dir-ap_run-01_epi.json
# /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth/sub-0085/ses-01/fmap/sub-0085_ses-01_acq-mb8_dir-ap_run-01_epi.json
