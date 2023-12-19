# %%
# load library
import os
from nilearn import plotting
from nilearn import datasets
from nilearn import image
import matplotlib.pyplot as plt
from pathlib import Path
import itertools
import sys, argparse
import glob

from bids import BIDSLayout

# help -----
# https://stackoverflow.com/questions/64331987/removing-hiding-empty-subplots-in-matplotlib-when-plotting-a-flexible-grid
# https://neurostars.org/t/multi-subjects-figures-with-nilearn-plotting/6042
# %% parameters ________________________________________________________________________
current_dir = os.getcwd()
# main_dir = Path(current_dir).parents[1] # discovery: /dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_social
# fmriprep_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'
main_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI'
fmriprep_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/'

# load image filename
# calculate mean image
parser = argparse.ArgumentParser()
parser.add_argument("--slurm-id", 
                    type=int, help="slurm id in numbers")
parser.add_argument("--task", 
                    type=str, help="BIDS task value")
parser.add_argument("--save_dir", 
                    type=str, help="Directory to save output")
# parser.add_argument("--pybids_db", 
#                     type=str, help="the pybids database to quickly load up your directory")

args = parser.parse_args()
slurm_id = args.slurm_id
task = args.task
save_dir = args.save_dir
# pybids_db = args.pybids_db

# %%
# Test Parameters:
# slurm_id=1
# qc_dir='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc'
# fmriprep_dir='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/'
# save_dir='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/'
# scratch_dir='/scratch/f003z4j'
# canlab_dir = '/dartfs-hpc/rc/lab/C/CANlab/modules/CanlabCore'
# task = ''
# pybids_db = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/1080_wasabi/1080_wasabi_BIDSLayout'
# %%
# Search for pybids databases and store the result in a variable
# pybids_db = search_for_pybids_database(pybids_db)

# if pybids_db:
#     print("A pybids database was found in directory:", pybids_db, "\n Database loaded.")
#     layout = BIDSLayout(fmriprep_dir, database_path=pybids_db)
# else:
#     print("No pybids database was found. \nGenerating a new database...this may take some time...")
#     layout = BIDSLayout(fmriprep_dir, database_path=os.path.join(fmriprep_dir, 'pybids_database'))

# %%
print(slurm_id)
# fmriprep_dir = '/Volumes/spacetop_data/derivatives/fmriprep/results/fmriprep'

# Get a list of subject directories in fmriprep_dir
subject_dirs = [name for name in os.listdir(fmriprep_dir) if os.path.isdir(os.path.join(fmriprep_dir, name)) and name.startswith('sub-')]

num_sessions_dict = {}
num_runs_dict = {}

for subject_dir in subject_dirs:
    subject_id = subject_dir.split("-")[-1]
    
    # Get a list of session directories for the current subject
    session_dirs = [name for name in os.listdir(os.path.join(fmriprep_dir, subject_dir)) if os.path.isdir(os.path.join(fmriprep_dir, subject_dir, name)) and name.startswith('ses-')]
    
    num_sessions = len(session_dirs)
    num_sessions_dict[subject_id] = num_sessions
    
    num_runs_dict[subject_id] = {}
    for session_dir in session_dirs:
        # Get a list of run directories for the current session
        run_dirs = [name for name in os.listdir(os.path.join(fmriprep_dir, subject_dir, session_dir)) if os.path.isdir(os.path.join(fmriprep_dir, subject_dir, session_dir, name))]
        
        num_runs = len(run_dirs)
        num_runs_dict[subject_id][session_dir] = num_runs


total_list = []


for subject_dir in subject_dirs:
    subject_id = subject_dir.split("-")[-1]
    
    # Get a list of session directories for the current subject
    session_dirs = [name for name in os.listdir(os.path.join(fmriprep_dir, subject_dir)) if os.path.isdir(os.path.join(fmriprep_dir, subject_dir, name)) and name.startswith('ses-')]
    
    for session_dir in session_dirs:
        # Get a list of files in the current session directory
        try:
            session_files = os.listdir(os.path.join(fmriprep_dir, subject_dir, session_dir, 'func'))
        except FileNotFoundError:
            print("No functional images found for subject", subject_dir, "session", session_dir, ". Skipping...")
            continue
        for session_file in session_files:
            # Check if the file is a functional image file (you can adjust the condition as needed)
            if session_file.endswith('.nii.gz') and 'bold' in session_file:
                # Extract the run number from the filename (assuming the filename follows a specific pattern)
                run_number = int(session_file.split('_run-')[1].split('_')[0])
                session_number = int(session_dir.split("-")[-1])
                
                total_list.append(('sub-' + subject_id, session_number, run_number))


# # Now you have the total_list containing tuples of (subject_id, session_number, run_number) for all subjects, sessions, and runs.

# # sub_list = next(os.walk(fmriprep_dir))[1]
# # sub_list = layout.get_subjects()
# sub_ind = sub_list[slurm_id]

# print(sub_ind)
# # sub_list = next(os.walk(csv_dir))[1]
# # ses_list = [1,3,4] #,3,4]
# # run_list = [1,2,3,4,5,6]
# # total_list = list(itertools.product([sub_ind], ses_list, run_list))

# ses_list = ['ses-' + str(session) for session in layout.get_sessions(subject=sub_ind.replace('sub-', ''))]
# run_list=layout.get_runs(subject=sub_ind.replace('sub-', ''))
# total_list = [('sub-'+sub_ind, int(ses), int(run)) 
#               for ses in layout.get_sessions(subject=sub_ind.replace('sub-', ''))
#               for run in layout.get_runs(subject=sub_ind.replace('sub-', ''), session=ses)]



# ses_list = ['ses-' + str(session) for session in range(1, num_sessions + 1)]  # Assuming you have 'num_sessions' defined
# run_list = list(range(1, num_runs + 1))  # Assuming you have 'num_runs' defined
# total_list = [('sub-'+sub_ind, int(ses.replace('ses-', '')), int(run))
#               for ses in ses_list
#               for run in run_list]


print(total_list)
# cuts = np.arange(i,j,k)
# create a figure with multiple axes to plot each anatomical image
# %%
# TODO: 
# fig, axes = plt.subplots(nrows=9, ncols=6, figsize=(14, 20))
# fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(14, 20))
# axes is a 2 dimensional numpy array
for i, (sub, ses, run) in enumerate(total_list):
    savedir = os.path.join( save_dir,sub)
    Path(savedir).mkdir(parents=True, exist_ok=True)
    print(sub, 'session: ',ses, 'run: ', run, 'iter: ', i)
# for ax in axes.flatten():
    # axes.flat[i]
    anatname = f"{sub}_acq-MPRAGEXp3X08mm_space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz"
    funcname = f"{sub}_ses-{ses:02d}_{task}*_acq-mb8_run-{run}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    funcpath_pattern = os.path.join(fmriprep_dir, sub, f"ses-{ses:02d}", "func", funcname)

    # This will return a list of all paths that match the pattern
    funcpaths = glob.glob(funcpath_pattern)

    anatpath = Path(os.path.join(fmriprep_dir, sub, "anat", anatname))
    subdir = Path(os.path.join(fmriprep_dir, sub))
    anat_pattern = '*preproc_T1w.nii.gz'
    
    # Check if the subject has anatomicals:
    if not anatpath.is_file():
        # Get a list of all items (files and directories) in the directory
        items_in_directory = os.listdir(subdir)

        # Filter out only the directories that start with 'ses-'
        ses_directories = [item for item in items_in_directory if item.startswith('ses-')]

        # Loop through each 'ses-' directory
        for ses_directory in ses_directories:
            ses_directory_path = os.path.join(subdir, ses_directory)
            anat_path = os.path.join(ses_directory_path, anat_folder)

            # Use glob to search for files that match the pattern '*preproc_T1w.nii.gz'
            matching_files = glob.glob(os.path.join(anat_path, anat_pattern))

            if matching_files:
                # If there are matching files, set anatpath to be the first matching file
                anatpath = matching_files[0]
                print(f"Found 'preproc_T1w.nii.gz' image in {anatpath}")
                break
            else:
                print(f"No 'preproc_T1w.nii.gz' image found in {ses_directory}")

        # If 'anatpath' is not set (i.e., no matching files found), handle accordingly
        if 'anatpath' not in locals():
            print("No 'preproc_T1w.nii.gz' image found in any 'ses-' directory.")
    
    # funcpath = Path(os.path.join(fmriprep_dir, sub, f"ses-{ses:02d}", "func", funcname))
    funcpath=Path(funcpaths[0]) # Take the first one only.

    # Split the path using the underscore character "_"
    path_parts = funcpath.stem.split('_')

    # Find the part that starts with "task-" and extract the task value
    taskname = next((part[len("task-"):] for part in path_parts if part.startswith("task-")), None)

    print(taskname)  # Output should be something like "bodymapST1"

    if funcpath.is_file():
        func = image.load_img(funcpath)
        anat = image.load_img(anatpath)

        meanimg = image.mean_img(func)
        # display = plotting.plot_anat(meanimg, axes=axes.flat[i], vmax = 300)
        # display = plotting.plot_stat_map(meanimg, axes=axes.flat[i], vmax = 300)
        display = plotting.plot_anat(anat)
        display = plotting.plot_stat_map(meanimg, 
                                        #  figure = fig, axes=axes.flat[i], 
                                        bg_img=anat,
                                         title = f"Sub: {sub}, Ses: {ses}, Run: {run}, Task: {taskname}", vmax=300, alpha = 0.5)

        # display.add_contours(meanimg, filled=False, alpha=0.7, colors='r')
        display.savefig(os.path.join(savedir, f"meanimg_{sub}_ses-{ses:02d}_run-{run:02d}.png"))
        print("plot")
