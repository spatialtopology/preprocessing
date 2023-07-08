import os
import shutil

source_directory = "/dartfs-hpc/scratch/f0042x1"  # Path to the source directory containing sub-0002 to sub-0133 folders
destination_directory = "/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/runwisecorr/"

for sub_folder in range(1, 134):
    sub_folder_name = f"sub-{str(sub_folder).zfill(4)}"
    source_path = os.path.join(source_directory, sub_folder_name)
    destination_path = os.path.join(destination_directory, sub_folder_name)
    
    # Check if the source subfolder exists
    if not os.path.exists(source_path):
        continue  # Skip to the next iteration if the subfolder doesn't exist
    
    os.makedirs(destination_path, exist_ok=True)  # Create the destination directory if it doesn't exist
    for file_name in os.listdir(source_path):
        if file_name.startswith("masked") and file_name.endswith(".png"):
            file_path = os.path.join(source_path, file_name)
            shutil.copy(file_path, destination_path)
