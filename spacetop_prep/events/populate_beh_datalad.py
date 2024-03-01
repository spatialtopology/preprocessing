# %%
import os, glob
from os.path import join
# %%
def extract_bids_metadata(filename):
    """
    Extract BIDS (Brain Imaging Data Structure) metadata from a given filename.

    Parameters:
    filename (str): The filename from which to extract metadata.

    Returns:
    dict: A dictionary containing the extracted metadata.
    """
    metadata = {}
    parts = filename.split('_')
    for part in parts:
        if part.startswith('sub'):
            metadata['bids_sub'] = part
        elif part.startswith('ses'):
            metadata['bids_ses'] = part
        elif part.startswith('task'):
            metadata['bids_task'] = part
        elif part.startswith('run'):
            metadata['bids_run'] = part.split('.')[0]  # Remove file extension if present

    return metadata

def copy_specific_files(filenames, source_dir, dest_dir):
    """
    Copy specific files from a source directory to a destination directory.

    Parameters:
    filenames (list): A list of filenames to copy.
    source_dir (str): The source directory where the files are located.
    dest_dir (str): The destination directory where the files should be copied.
    """
    # Ensure the destination directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Copy each file
    for filename in filenames:
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        # Check if the source file exists before attempting to copy
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"File {filename} copied successfully.")
        else:
            print(f"File {filename} does not exist in the source directory.")

# %%
# Test the function with the provided filename
filename = "sub-0064_ses-04_task-tomsaxe_run-02_events.tsv"
metadata = extract_bids_metadata(filename)
metadata



# where is the curated behavioral data at
datalad_dir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/'
beh_tmp_dir = join(datalad_dir, 'dartmouth/beh_TMP')
# identify the filename
flist = glob.glob(join(beh_tmp_dir, "*.tsv"))
# extract metadata
for filename in flist:
    # filename = "sub-0064_ses-04_task-tomsaxe_run-02_events.tsv"
    metadata = extract_bids_metadata(filename)
    metadata['bids_sub']
# create corresponding folder
    dest_dir = join(datalad_dir, 'dartmouth', metadata['bids_sub'], metadata['bids_ses'])

    copy_specific_files(filename, datalad_dir, dest_dir)
# populate folder with json and tsv