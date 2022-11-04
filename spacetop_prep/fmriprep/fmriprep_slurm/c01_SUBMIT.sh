#!/bin/bash

ml purge
ml singularity/3.3.0

#set your subjects
subjects=("sub-01" "sub-02" "sub-03" "sub-04" "sub-05" "sub-06" "sub-07" "sub-08" "sub-09" "sub-10")
#loop over your subject
for subj in ${subjects[*]}; do
    sbatch fmriprep_singularity.sh ${subj}
    sleep 1 # pause to be kind to the scheduler
done
