find . -type f -name '*dup-01*' -delete
datalad get .
BIDS_DIRECTORY="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth"
GUID_MAPPING="/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts/spacetop_prep/nda/GUIDMAPPING.txt"
OUTPUT_DIRECTORY="/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cueNDA"
bids2nda ${BIDS_DIRECTORY} ${GUID_MAPPING} ${OUTPUT_DIRECTORY}
