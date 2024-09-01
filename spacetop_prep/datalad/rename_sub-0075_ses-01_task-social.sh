#!/bin/bash
set -eu

# Define the rename function (assuming it's located at ../../../code/rename_file)
RENAME_FUNC="/Users/h/Documents/projects_local/1076_spacetop/code/rename_file"

# Define the base file name pattern
SUBPATH="/Users/h/Documents/projects_local/1076_spacetop/sub-0075/ses-01/func"
PATTERN="sub-0075_ses-01_task-social_acq-mb8_run"

# Rename files
$RENAME_FUNC "${SUBPATH}/${PATTERN}-04_bold.json" "${SUBPATH}/${PATTERN}-06_bold.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-04_bold.nii.gz" "${SUBPATH}/${PATTERN}-06_bold.nii.gz"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-04_sbref.json" "${SUBPATH}/${PATTERN}-06_sbref.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-04_sbref.nii.gz" "${SUBPATH}/${PATTERN}-06_sbref.nii.gz"

$RENAME_FUNC "${SUBPATH}/${PATTERN}-03_bold.json" "${SUBPATH}/${PATTERN}-04_bold.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-03_bold.nii.gz" "${SUBPATH}/${PATTERN}-04_bold.nii.gz"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-03_sbref.json" "${SUBPATH}/${PATTERN}-04_sbref.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-03_sbref.nii.gz" "${SUBPATH}/${PATTERN}-04_sbref.nii.gz"

$RENAME_FUNC "${SUBPATH}/${PATTERN}-02_bold.json" "${SUBPATH}/${PATTERN}-03_bold.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-02_bold.nii.gz" "${SUBPATH}/${PATTERN}-03_bold.nii.gz"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-02_sbref.json" "${SUBPATH}/${PATTERN}-03_sbref.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-02_sbref.nii.gz" "${SUBPATH}/${PATTERN}-03_sbref.nii.gz"

$RENAME_FUNC "${SUBPATH}/${PATTERN}-01_bold.json" "${SUBPATH}/${PATTERN}-02_bold.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-01_bold.nii.gz" "${SUBPATH}/${PATTERN}-02_bold.nii.gz"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-01_sbref.json" "${SUBPATH}/${PATTERN}-02_sbref.json"
$RENAME_FUNC "${SUBPATH}/${PATTERN}-01_sbref.nii.gz" "${SUBPATH}/${PATTERN}-02_sbref.nii.gz"
