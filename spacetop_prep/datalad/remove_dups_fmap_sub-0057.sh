#!/bin/bash

# Function to handle renaming for a given direction
rename_fmapdup() {
    local DIRECTION="$1"
    local RUN_NUM_ORIG="$2"
    local RUN_NUM_NEW="$3"

    # Construct original and new JSON filenames based on direction and run numbers
    local DUPJSON="./sub-0057/ses-01/fmap/sub-0057_ses-01_acq-mb8_dir-${DIRECTION}_run-${RUN_NUM_ORIG}_epi__dup-01.json"
    local RENAMEJSON="./sub-0057/ses-01/fmap/sub-0057_ses-01_acq-mb8_dir-${DIRECTION}_run-${RUN_NUM_NEW}_epi.json"

    # Rename the JSON file
    datalad run ../../../code/rename_file "${DUPJSON}" "${RENAMEJSON}"

    # Construct the corresponding .nii.gz filenames
    local ORIGINAL_NII_GZ="${DUPJSON%.json}.nii.gz"
    local NEW_NII_GZ="${RENAMEJSON%.json}.nii.gz"

    # Check if the original .nii.gz file exists before attempting to rename
    if [ -f "$ORIGINAL_NII_GZ" ]; then
        # Rename the .nii.gz file
        git mv "$ORIGINAL_NII_GZ" "$NEW_NII_GZ"
        echo "Renamed $ORIGINAL_NII_GZ to $NEW_NII_GZ"
    else
        echo "File $ORIGINAL_NII_GZ does not exist, skipping..."
    fi
}

# Run the renaming for both directions
# Adjust RUN_NUM_ORIG and RUN_NUM_NEW as needed for each case
rename_fmapdup "ap" "02" "03"
rename_fmapdup "pa" "02" "03" # Update RUN_NUM_ORIG and RUN_NUM_NEW as per your requirements for the pa direction
