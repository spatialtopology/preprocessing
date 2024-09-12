# load badrun json
# query specific run by opening run specific csv
# extract value
# save in corresponding dataframe
# TODO: compile mean values
# %%
import nilearn
import pandas as pd 
import matplotlib.pyplot as plt
import os, glob, sys
import numpy as np
import seaborn as sns
import re
import nibabel as nib
import json
# %%
print("load bad data metadata")
with open("/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/qcplot/boldcorrelation/bad_runs.json", "r") as json_file:
    bad_dict = json.load(json_file)
# %%
# Convert JSON data to DataFrame
rows = []
for subject, runs in bad_dict.items():
    for run in runs:
        row = {'Subject': subject, 'Run': run}
        rows.append(row)

df = pd.DataFrame(rows)

print(df)
# Separate 'Run' column into 'Session' and 'Run' columns
df['sub'] = df['Subject'].str.extract(r'sub-(\d+)', expand=False).astype(int)
df['ses'] = df['Run'].str.extract(r'ses-(\d+)', expand=False).astype(int)
df['run'] = df['Run'].str.extract(r'run-(\d+)', expand=False).astype(int)

print(df)

# %%
# loop through dataframe and query the correlation coefficients of the corresponding row. 
subset = pd.DataFrame(df.iloc[1]).T
for index, row in df.iterrows():
    sub = f"sub-{row['sub']:04d}"
    corrdf = pd.read_csv(f'/Volumes/derivatives/fmriprep_qc/runwisecorr/{sub}/{sub}_runwisecorrelation.csv')
    corr_values = corrdf.loc[:, f"ses-{row['ses']:02d}_run-{row['run']:02d}"]
    df.loc[index, 'mean_corr'] = np.mean(corr_values)
# %%

# bad_runs = []
# if bad_dict.get(sub, 'empty') != 'empty':
#     bad_runs = bad_dict[sub]

# runwisecorr_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr/sub-0047/sub-0047_runwisecorrelation.csv'

# %%
print("load bad data metadata")
with open("/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/qcplot/not_in_intendedFor.json", "r") as json_file:
    nofieldmap = json.load(json_file)
# %%
# Convert JSON data to DataFrame
rows = []
for subject, runs in bad_dict.items():
    for run in runs:
        row = {'Subject': subject, 'Run': run}
        rows.append(row)

df = pd.DataFrame(rows)

print(df)
# Separate 'Run' column into 'Session' and 'Run' columns
df['sub'] = df['Subject'].str.extract(r'sub-(\d+)', expand=False).astype(int)
df['ses'] = df['Run'].str.extract(r'ses-(\d+)', expand=False).astype(int)
df['run'] = df['Run'].str.extract(r'run-(\d+)', expand=False).astype(int)

print(df)

# %%
# loop through dataframe and query the correlation coefficients of the corresponding row. 
subset = pd.DataFrame(df.iloc[1]).T
for index, row in df.iterrows():
    sub = f"sub-{row['sub']:04d}"
    corrdf = pd.read_csv(f'/Volumes/derivatives/fmriprep_qc/runwisecorr/{sub}/{sub}_runwisecorrelation.csv')
    corr_values = corrdf.loc[:, f"ses-{row['ses']:02d}_run-{row['run']:02d}"]
    df.loc[index, 'mean_corr'] = np.mean(corr_values)
# %%