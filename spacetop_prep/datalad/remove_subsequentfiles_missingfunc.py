import os
import glob

datalad_dir = '/Users/h/Documents/projects_local/1076_spacetop'
# Define the suffixes for the different file types
file_suffixes = ['_bold.json', '_bold.nii.gz', '_events.tsv', '_sbref.json', '_sbref.nii.gz']

# List all files in the current directory

folders = glob.glob(os.path.join(datalad_dir, 'sub-*'))
sublist = sorted([os.path.basename(x) for x in folders])

for sub in sublist:

    files = glob.glob(os.path.join(datalad_dir, sub, 'ses-*', 'func', '*' ))

    # Dictionary to keep track of files grouped by their base name
    file_dict = {}

    for file in files:
        # Strip .gz if present
        base_name, suffix = os.path.splitext(file)
        if suffix == '.gz':
            base_name, _ = os.path.splitext(base_name)  # remove the .gz suffix

        # Determine the base name
        for suffix in file_suffixes:
            if file.endswith(suffix):
                base_name = file[:-len(suffix)]  # remove the suffix
                break

        # Group files by their base name
        if base_name not in file_dict:
            file_dict[base_name] = []
        file_dict[base_name].append(file)

    # Process each base name group
    for base_name, file_list in file_dict.items():
        # Check if _bold.nii.gz exists
        bold_nifti_exists = any(f.endswith('_bold.nii.gz') for f in file_list)
        
        if not bold_nifti_exists:
            # If no _bold.nii.gz file exists, remove all files in this group
            for file in file_list:
                print(f"{file_list}")
                print(f"Removing file: {file}")
                #os.remove(file)

    print("Cleanup completed.")
