import os 
import glob
from pathlib import Path
import shutil
import re
import traceback


# %% directories ___________________________________
current_dir = os.getcwd()
main_dir = Path(current_dir).parents[1]
main_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop'
print(main_dir)

acq_list = glob.glob(os.path.join(main_dir, 'biopac', 'dartmouth', 'rawdata', '**', '*.acq'), recursive = True)
# if __name__ == "__main__":
    # try:
for acq in acq_list:
    try: 
        filename  = os.path.basename(acq)
        sub = [match for match in filename.split('_') if "sub" in match][0] # 'sub-0056'
        ses = [match for match in filename.split('_') if "ses" in match][0] # 'ses-03'
        task = [match for match in filename.split('_') if "task" in match][0]

        print(sub, ses, task)
        new_dir = os.path.join(main_dir,'biopac','dartmouth','b02_sorted',sub,ses)
        Path(new_dir).mkdir(parents=True,exist_ok=True )
        shutil.copy(acq,new_dir)

    except:
        with open("exceptions.log", "a") as logfile:
            traceback.print_exc(file=logfile)
