#!/bin/bash

# Original and new JSON filenames
DUPJSON="./sub-0057/ses-01/fmap/sub-0057_ses-01_acq-mb8_dir-ap_run-02_epi__dup-01.json"
RENAMEJSON="./sub-0057/ses-01/fmap/sub-0057_ses-01_acq-mb8_dir-ap_run-03_epi.json"

# Rename the JSON file
datalad run ../../../code/rename_file "${DUPJSON}" "${RENAMEJSON}"

# Construct the corresponding .nii.gz filenames
# For the original file
ORIGINAL_NII_GZ="${DUPJSON%.json}.nii.gz"
# For the new file
NEW_NII_GZ="${RENAMEJSON%.json}.nii.gz"

# Check if the original .nii.gz file exists before attempting to rename
if [ -f "$ORIGINAL_NII_GZ" ]; then
    # Rename the .nii.gz file
    mv "$ORIGINAL_NII_GZ" "$NEW_NII_GZ"
    echo "Renamed $ORIGINAL_NII_GZ to $NEW_NII_GZ"
else
    echo "File $ORIGINAL_NII_GZ does not exist, skipping..."
fi
