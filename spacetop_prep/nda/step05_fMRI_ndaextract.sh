
BIDS_DIRECTORY="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep"
GUID_MAPPING="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep/nda/ndar_subject.csv"
OUTPUT_DIRECTORY="/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cueNDA"
bids2nda ${BIDS_DIRECTORY} ${GUID_MAPPING} ${OUTPUT_DIRECTORY}