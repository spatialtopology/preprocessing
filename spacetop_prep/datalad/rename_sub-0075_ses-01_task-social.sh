#!/bin/bash
set -eu

# Define the rename function (assuming it's located at ../../../code/rename_file)
RENAME_FUNC="/Users/h/Documents/projects_local/1076_spacetop/code/rename_file"

# Define the base file name pattern
PATTERN="sub-0075_ses-01_task-social_acq-mb8_run"

# Rename files
$RENAME_FUNC "${PATTERN}-01_bold.json" "${PATTERN}-02_bold.json"
$RENAME_FUNC "${PATTERN}-01_bold.nii.gz" "${PATTERN}-02_bold.nii.gz"
$RENAME_FUNC "${PATTERN}-01_sbref.json" "${PATTERN}-02_sbref.json"
$RENAME_FUNC "${PATTERN}-01_sbref.nii.gz" "${PATTERN}-02_sbref.nii.gz"

$RENAME_FUNC "${PATTERN}-02_bold.json" "${PATTERN}-03_bold.json"
$RENAME_FUNC "${PATTERN}-02_bold.nii.gz" "${PATTERN}-03_bold.nii.gz"
$RENAME_FUNC "${PATTERN}-02_sbref.json" "${PATTERN}-03_sbref.json"
$RENAME_FUNC "${PATTERN}-02_sbref.nii.gz" "${PATTERN}-03_sbref.nii.gz"

$RENAME_FUNC "${PATTERN}-03_bold.json" "${PATTERN}-04_bold.json"
$RENAME_FUNC "${PATTERN}-03_bold.nii.gz" "${PATTERN}-04_bold.nii.gz"
$RENAME_FUNC "${PATTERN}-03_sbref.json" "${PATTERN}-04_sbref.json"
$RENAME_FUNC "${PATTERN}-03_sbref.nii.gz" "${PATTERN}-04_sbref.nii.gz"

# The run-06 files do not need renaming
