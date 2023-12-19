
# %%

import neurokit2 as nk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys, glob
import pathlib 
import numpy as np

import itertools

plt.rcParams['figure.figsize'] = [15, 5]  # Bigger images
plt.rcParams['font.size']= 14

pwd = os. getcwd()
main_dir = pathlib.Path(pwd).parents[1]
data_dir = '/Users/h/Dropbox/projects_dropbox/spacetop_biopac'

sys.path.append(os.path.join(main_dir, 'biopac'))
sys.path.insert(0,os.path.join(main_dir, 'biopac'))
print(sys.path)
import utils



# %% Get data

# sub-0053
# ses-03

sub_num = 51
ses_num = 3
run_num = 4
sub = f"sub-{sub_num:04d}"
ses = f"ses-{ses_num:02d}"
run = f"run-{run_num-1:02d}"
physio_fname = os.path.join(data_dir, 'data', sub, ses, 'physio', f"SOCIAL_spacetop_{sub}_{ses}_task-social_ANISO.acq")
beh_fname = glob.glob(os.path.join(data_dir, 'data', sub, ses, 'beh', f"{sub}_{ses}_task-social_{run}-*_beh.csv"))[0]


# %% load data
print("load physio data...")
physio_df, spacetop_samplingrate = nk.read_acqknowledge(physio_fname)
print("check physio data columns: ",physio_df.columns)
beh_df = pd.read_csv(beh_fname)


# %% identify run transition
utils.preprocess._binarize_channel(df = physio_df, 
                        source_col = 'trigger', 
                        new_col = 'fmri_trigger', 
                        threshold= None,
                        binary_high=5, 
                        binary_low=0)

df_transition = utils.preprocess._identify_boundary(df = physio_df, 
                        binary_col = 'fmri_trigger', 
                        event_name = 'experiment')
run_df = utils.preprocess._extract_runs(df = physio_df,
                        dict = df_transition,  run_num = run_num)

# %%
