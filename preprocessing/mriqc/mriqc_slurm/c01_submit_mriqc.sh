ingularity/3.3.0

#set your subjects
subjects=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10" \
"11" "12" "13" "14" "15" "16" "17" "18" "19" "20" \
"21" "22" "23" "24" "25" "26" "27" "28" "29" "30" \
"31" "32" "33")

#loop over your subject
for subj in ${subjects[*]}; do
    sbatch mriqc_singularity.sh ${subj}
    sleep 1 # pause to be kind to the scheduler
done
