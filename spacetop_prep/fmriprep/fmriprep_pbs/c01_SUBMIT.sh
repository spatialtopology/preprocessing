#!/bin/bash
#PBS -N fmriprep_submit
#PBS -q default
#PBS -l nodes=1:ppn=8
#PBS -l walltime=01:00:00
#PBS -m bea


subjects=("sub-01" "sub-02" "sub-03" "sub-04" "sub-05" \
 "sub-06" "sub-07" "sub-08" "sub-09" "sub-10" \
 "sub-11" "sub-12" "sub-13" "sub-14" "sub-15" \
 "sub-16" "sub-17" "sub-18" "sub-19" "sub-20" \
 "sub-21" "sub-22" "sub-23" "sub-24" "sub-25" \
 "sub-26" "sub-27" "sub-28" "sub-29" "sub-30" \
 "sub-31" "sub-32" "sub-33")

main_dir=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/conformity.01
for SUB in ${subjects[*]}; do
        mksub ${main_dir}/scripts/fmriprep/submit_fmriprep.pbs -F ${SUB}
        echo "submitting ${SUB}"
        sleep 1
done
echo "Done submitting jobs!"
