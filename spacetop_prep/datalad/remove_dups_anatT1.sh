#!/bin/bash
## TODO: change the file so that the dup is the earlier scan
## the latter scan should be better. always. 

# Define a file to log errors
# error_log="error_log_funcanat.txt"

LOG_FILE="anat_error_log.txt"
if [ -f "$LOG_FILE" ]; then
    rm "$LOG_FILE"
fi


SUMMARYLOG_FILE="anat_summary_log.txt"
if [ -f "$SUMMARYLOG_FILE" ]; then
    rm "$SUMMARYLOG_FILE"
fi

dup_files=()
while IFS= read -r -d $'\n' file; do
    dup_files+=("$file")
done < <(find . -path "*/anat/*__dup-*.json")

# Loop through each file found.
for DUPJSON in "${dup_files[@]}"; do
    # Use jq to extract TR values.
    DUPJSON_TR=$(jq '.AcquisitionTime' "${DUPJSON}")
    PRIMARYJSON=$(echo "${DUPJSON}" | sed 's/__dup-[0-9]*//')
    PRIMARYJSON_TR=$(jq '.AcquisitionTime' "${PRIMARYJSON}")
    if [[ "$PRIMARYJSON_TR" == "null" || "$PRIMARYJSON_TR" =~ "error" ]]; then
        echo "$PRIMARYJSON: Error extracting TR value." >> "$error_log"
        continue
    fi
PRIMARYJSON_NODEC=${PRIMARYJSON_TR%%.*}
DUPJSON_NODEC=${DUPJSON_TR%%.*}
    PRIMARYJSON_SEC=$(echo $PRIMARYJSON_NODEC |  tr -d '"'| awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
    DUPJSON_SEC=$(echo $DUPJSON_NODEC |  tr -d '"' | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')

    # Compare the numeric values
    #if (( $(echo "$PRIMARYJSON_SEC < $DUPJSON_SEC" |bc -l) )); then
    if [ "$PRIMARYJSON_SEC" -lt "$DUPJSON_SEC" ]; then
	echo -e "\n${DUPJSON}\nPRIMARYJSON acquisition time is earlier." >> $LOG_FILE
        echo -e "\n>>>>> ERROR: PRIMARYJSON ${PRIMARYJSON_NODEC} ${PRIMARYJSON_SEC} has an earlier time than DUPJSON ${DUPJSON_NODEC} ${DUPJSON_SEC}\n\n" >> $LOG_FILE

        # SWAP DUP AND PRIMARY, THEN DELETED
        PRIMARYGZ=${PRIMARYJSON}
        DUPGZ=${DUPJSON} #TODO remove file extension

    elif [ "$PRIMARYJSON_SEC" -gt "$DUPJSON_SEC" ]; then
    #elif (( $(echo "$PRIMARYJSON_SEC > $DUPJSON_SEC" |bc -l) )); then
        echo -e "\nDUPJSON acquisition time is earlier." >> $LOG_FILE
        echo -e "Info: DUPJSON is identified as the correct file due to earlier acquisition time." >> $SUMMARYLOG_FILE
        # generic_filename=$(echo "$DUPJSON" | sed -E 's/(run-[0-9]+_).+(__dup-[0-9]+).*/\1*\2.*/')
        # basename=$(basename "$DUPJSON" | sed 's/\.[^.]*$//')
        basename=$(basename "$DUPJSON" | sed 's/\.[^.]*$//')
        directory=$(dirname "$DUPJSON")
        echo -e "$directory"
        echo -e "$basename"
        related_files=$(find "$directory" -name "${basename}*" -print)

        # Print and remove the related files
        echo -e "Removed files: ${related_files}\n\n" >> "$LOG_FILE"
        for rm_file in $related_files; do
            echo "Removing: $rm_file"
            git rm "$rm_file"
        done
        # generic_filename=$(find "$directory" -type f -name "${basename}*" -print)

        # read -a files_to_remove <<< "$generic_filename"
        # echo -e "removed files: ${generic_filename}\n\n" >> $LOG_FILE
        # # Loop through the array and remove each file
        # for rm_file in "${files_to_remove[@]}"; do
        #     echo "remove!"
        #     git rm "$rm_file"
        # done
    else
        echo -e "\n${DUPJSON}\nAcquisition times are the same." >> $LOG_FILE
        # Log as error or info since times being the same might be unexpected
        echo -e "Warning: PRIMARYJSON ${PRIMARYJSON_SEC} ${PRIMARYJSON_NODEC} and DUPJSON ${DUPJSON_SEC} ${DUPJSON_NODEC} have the same acquisition time.\n\n" >> $LOG_FILE
    fi

done

