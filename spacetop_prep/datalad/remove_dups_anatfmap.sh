#!/bin/bash
## TODO: change the file so that the dup is the earlier scan
## the latter scan should be better. always. 



# Define a file to log errors
# error_log="error_log_funcanat.txt"
LOG_FILE="fmap_error_log.txt"
if [ -f "$LOG_FILE" ]; then
    rm "$LOG_FILE"
fi
# mapfile -t dup_files < <(find . -type f -name '*__dup-*')

dup_files=()
while IFS= read -r -d $'\n' file; do
    dup_files+=("$file")
done < <(find . -type f -path "*/fmap/*__dup-*.json")

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
#PRIMARYJSON_SEC=$(echo $PRIMARYJSON_TR | awk -F: '{ split($3, a, "."); print ($1 * 3600) + ($2 * 60) + a[1] }')
#DUPJSON_SEC=$(echo $DUPJSON_TR | awk -F: '{ split($3, a, "."); print ($1 * 3600) + ($2 * 60) + a[1] }')

    # Compare the numeric values
    #if (( $(echo "$PRIMARYJSON_SEC < $DUPJSON_SEC" |bc -l) )); then
    if [ "$PRIMARYJSON_SEC" -lt "$DUPJSON_SEC" ]; then
	echo -e "\n${DUPJSON}\nPRIMARYJSON acquisition time is earlier." >> $LOG_FILE
        echo -e "Error: PRIMARYJSON ${PRIMARYJSON_NODEC} ${PRIMARYJSON_SEC} has an earlier time than DUPJSON ${DUPJSON_NODEC} ${DUPJSON_SEC}\n\n" >> $LOG_FILE
    elif [ "$PRIMARYJSON_SEC" -gt "$DUPJSON_SEC" ]; then
    #elif (( $(echo "$PRIMARYJSON_SEC > $DUPJSON_SEC" |bc -l) )); then
        echo -e "\nDUPJSON acquisition time is earlier." >> $LOG_FILE
        echo -e "Info: DUPJSON is identified as the correct file due to earlier acquisition time." >> $LOG_FILE
        generic_filename=$(echo "$DUPJSON" | sed -E 's/(run-[0-9]+_).+(__dup-[0-9]+).*/\1*\2.*/')
        read -a files_to_remove <<< "$generic_filename"
        echo -e "removed files: ${generic_filename}\n\n" >> $LOG_FILE
        # Loop through the array and remove each file
        for rm_file in "${files_to_remove[@]}"; do
            echo "remove!"
            # git rm "$rm_file"
        done
    else
        echo -e "\n${DUPJSON}\nAcquisition times are the same." >> $LOG_FILE
        # Log as error or info since times being the same might be unexpected
        echo -e "Warning: PRIMARYJSON ${PRIMARYJSON_SEC} ${PRIMARYJSON_NODEC} and DUPJSON ${DUPJSON_SEC} ${DUPJSON_NODEC} have the same acquisition time.\n\n" >> $LOG_FILE
    fi

done


#     # Initialize a flag to indicate a matching key has been found.
#     found_match=0

#     # Attempt to extract a meaningful part of the filename to match against array keys.
#     filename=$(basename "$DUPJSON")
#     filename=${filename%__dup-*}

#     # Iterate over keys in myArray.
#     for key in "${!myArray[@]}"; do
#         if [[ "$filename" == *"$key"* ]]; then
#             found_match=1
#             EXPECTED_TR=${myArray[$key]}
#             echo "Found matching key: $key with TR: $EXPECTED_TR for file $DUPJSON"
#             if [[ "$PRIMARYJSON_TR" -eq "$EXPECTED_TR" && "$DUPJSON_TR" -lt "$PRIMARYJSON_TR" ]]; then
#                 echo "Conditions met for $DUPJSON. Removing file."
#                 # Uncomment the next line to perform file removal
                
#                 # generic_filename=$(echo "$DUPJSON" | sed -E 's/(run-[0-9]+_).+(__dup-.+)/\1*\2/')
#             generic_filename=$(echo "$DUPJSON" | sed -E 's/(run-[0-9]+_).+(__dup-[0-9]+).*/\1*\2.*/')
#             read -a files_to_remove <<< "$generic_filename"

#             # Loop through the array and remove each file
#             for rm_file in "${files_to_remove[@]}"; do
#                 git rm "$rm_file"
#             done

#             else
#                 # Handle errors
#                 if [[ "$DUPJSON_TR" -ge "$PRIMARYJSON_TR" ]]; then
#                     echo "$DUPJSON: DUPJSON_TR (${DUPJSON_TR}) is not smaller than PRIMARYJSON_TR (${PRIMARYJSON_TR})." >> "$error_log"
#                 fi
#                 if [[ "$PRIMARYJSON_TR" -ne "$EXPECTED_TR" ]]; then
#                     echo "$PRIMARYJSON: PRIMARYJSON_TR (${PRIMARYJSON_TR}) does not match EXPECTED_TR ($EXPECTED_TR)." >> "$error_log"
#                 fi
#             fi
#             break
#         fi
#         done           
#     if [[ $found_match -eq 0 ]]; then
#         echo "No matching key found in the array for $DUPJSON"
#     fi
# done 
