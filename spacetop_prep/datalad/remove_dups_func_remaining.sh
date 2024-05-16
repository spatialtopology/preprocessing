# Declare an associative array
declare -A myArray=(
["task-narratives_acq-mb8_run-01"]=967
["task-narratives_acq-mb8_run-02"]=1098
["task-narratives_acq-mb8_run-03"]=1298
["task-narratives_acq-mb8_run-04"]=1156
["task-social"]=872
["task-fractional_acq-mb8_run-01"]=1323
["task-fractional_acq-mb8_run-02"]=1322
["task-shortvideo"]=1616
["task-faces"]=914
["ses-01_task-alignvideo_acq-mb8_run-01"]=1073
["ses-01_task-alignvideo_acq-mb8_run-02"]=1376
["ses-01_task-alignvideo_acq-mb8_run-03"]=1016
["ses-01_task-alignvideo_acq-mb8_run-04"]=1209
["ses-02_task-alignvideo_acq-mb8_run-01"]=839
["ses-02_task-alignvideo_acq-mb8_run-02"]=1859
["ses-02_task-alignvideo_acq-mb8_run-03"]=1158
["ses-02_task-alignvideo_acq-mb8_run-04"]=914
["ses-03_task-alignvideo_acq-mb8_run-01"]=1157
["ses-03_task-alignvideo_acq-mb8_run-02"]=1335
["ses-03_task-alignvideo_acq-mb8_run-03"]=1065
["ses-04_task-alignvideo_acq-mb8_run-01"]=1268
["ses-04_task-alignvideo_acq-mb8_run-02"]=926
)
# Access an element using its key
echo "The value of key1 is: ${myArray["ses-04_task-alignvideo_acq-mb8_run-02"]}"

# Iterate over keys and values of the array
for key in "${!myArray[@]}"; do
    echo "Key: $key, Value: ${myArray[$key]}"
done

# Define a file to log errors
error_log="errorlog_BOLD_DUP.txt"

# find files that match file template
dup_files=()
while IFS= read -r -d $'\n' file; do
    dup_files+=("$file")
done < <(find . -path './.sourcedata' -prune -o -name '*bold__dup-*.json')

# Loop through each file found.
for DUPJSON in "${dup_files[@]}"; do
    # Use jq to extract TR values and acquisition time
    BOLDJSON=$(echo "${DUPJSON}" | sed 's/__dup-[0-9]*//')
    BOLDJSON_TR=$(jq '.dcmmeta_shape[3]' "${BOLDJSON}")
    DUPJSON_TR=$(jq '.dcmmeta_shape[3]' "${DUPJSON}")
    BOLDJSON_TIME=$(jq '.AcquisitionTime' "${BOLDJSON}")
    DUPJSON_TIME=$(jq '.AcquisitionTime' "${DUPJSON}")

    DUPJSONFNAME=$(basename "$DUPJSON")
    BOLDJSONFNAME=$(basename "$BOLDJSON")
    directory=$(dirname "$DUPJSON")
    SBREFJSON="${directory}/${BOLDJSONFNAME/bold/sbref}"
    DUPSBREFJSON="${directory}/${DUPJSONFNAME/bold/sbref}"

    if [[ "$BOLDJSON_TR" == "null" || "$BOLDJSON_TR" =~ "error" ]]; then
        echo "$BOLDJSON: Error extracting TR value." >> "$error_log"
        continue
    fi

    # check the time of each file
    BOLDJSON_NODEC=${BOLDJSON_TIME%%.*}
    DUPJSON_NODEC=${DUPJSON_TIME%%.*}
    BOLDJSON_SEC=$(echo $BOLDJSON_NODEC |  tr -d '"'| awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
    DUPJSON_SEC=$(echo $DUPJSON_NODEC |  tr -d '"' | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')

    # Initialize a flag to indicate a matching key has been found.
    found_match=0

    # Attempt to extract a meaningful part of the filename to match against array keys.
    filename=$(basename "$DUPJSON")
    filename=${filename%__dup-*}

    # Iterate over keys in myArray.
    for key in "${!myArray[@]}"; do
        if [[ "$filename" == *"$key"* ]]; then
            found_match=1
            EXPECTED_TR=${myArray[$key]}
            echo "Found matching key: $key with TR: $EXPECTED_TR for file $DUPJSON"

            # CASE 1: BOLD is primary
            # - BOLD TR == expected TR [TRUE]
            # - DUP TR  == expected TR [NA]
            # - DUP TR < BOLD [TRUE]
            # - DUP hour time is later than BOLD (BOLDJSON_SEC)[NA]
            if [[ "$BOLDJSON_TR" -eq "$EXPECTED_TR" && \
                "$DUPJSON_TR" -lt "$BOLDJSON_TR" ]]; then
                echo -e "\nCASE 1: BOLD is primary; delete DUPS"
                echo -e "\tConditions met for $DUPJSON. Removing file."
                generic_filename=$(echo "$DUPJSON" | sed -E 's/(run-[0-9]+_).+(__dup-[0-9]+).*/\1*\2.*/')
                read -a files_to_remove <<< "$generic_filename"
                # Loop through the array and remove each file
                for rm_file in "${files_to_remove[@]}"; do
                    ######################### TST START #########################
                    echo -e "\tREMOVE: $rm_file"
                    # git rm "$rm_file"
                    ######################### TST END #########################
                done

            else
                # CASE 2: DUP is primary
                # - [FALSE] BOLD TR == expected TR ->  BOLD TR ne expected TR
                # - [ TRUE] DUP TR  == expected TR
                # - [FALSE] DUP TR < BOLD, -> DUP ge BOLD
                # - [ TRUE] DUP hour time is later than BOLD (BOLDJSON_SEC)
                if [[ "$BOLDJSON_TR" -ne "$EXPECTED_TR" && \
                "$DUPJSON_TR" -eq "$EXPECTED_TR" && \
                "$DUPJSON_TR" -ge "$BOLDJSON_TR" && \
                "$BOLDJSON_SEC" -lt "$DUPJSON_SEC" ]]; then
                    echo -e "\nCASE 2: DUP is primary"
                    echo -e "\t$BOLDJSON"
                    echo -e "\t* $BOLDJSON: BOLDJSON_TR (${BOLDJSON_TR}) does not match expected TR (${EXPECTED_TR})." >> "$error_log"
                    echo -e "\t* $DUPJSON: DUPJSON_TR (${DUPJSON_TR}) matches expected TR (${EXPECTED_TR})." >> "$error_log"
                    echo -e "\t* $DUPJSON: DUPJSON_TR (${DUPJSON_TR}) is not smaller than BOLDJSON_TR (${BOLDJSON_TR})." >> "$error_log"
                    echo -e "\t* $DUPJSON: DUPJSON (${DUPJSON_SEC}) is acquired later than BOLDJSON (${BOLDJSON_SEC})." >> "$error_log"
                    echo -e "\tDUPJSON is the primary file/ rename and resolve"

                    # rename BOLD.json
                    # echo "\t*CHANGE FILENAME: ${DUPJSON} -> ${BOLDJSON}"
                    # echo "\t*CHANGE FILENAME: ${DUPNII} -> ${BOLDNII}"
                    # echo "\t*CHANGE FILENAME: ${DUPSBREFJSON} -> ${SBREFJSON}"
                    # echo "\t*CHANGE FILENAME: ${DUPSBREFNII} -> ${SBREFNII}"

                    ######################### TST START #########################
                    # $(dirname "$0")/rename_file "${BOLDJSON}" PURGEJSON; 
                    # $(dirname "$0")/rename_file "${DUPJSON}" "${BOLDJSON}"; 
                    # $(dirname "$0")/rename_file PURGEJSON "${DUPJSON}"

                    # # find SBREF
                    # # rename BOLD.nii
                    # $(dirname "$0")/rename_file "${SBREFJSON}" PURGESBREFJSON; 
                    # $(dirname "$0")/rename_file "${DUPSBREFJSON}" "${SBREFJSON}"; 
                    # $(dirname "$0")/rename_file PURGESBREFJSON "${DUPSBREFJSON}"
                    ######################### TST END #########################
                fi


                # - [FALSE] BOLD TR == expected TR ->  BOLD TR ne expected TR
                # - [FALSE] DUP TR  == expected TR
                # - [FALSE] DUP TR < BOLD, -> DUP ge BOLD
                # - [ TRUE] DUP hour time is later than BOLD (BOLDJSON_SEC)
                if [[ "$BOLDJSON_TR" -ne "$EXPECTED_TR" && \
                "$DUPJSON_TR" -ne "$EXPECTED_TR" ]]; then
                    echo -e "\nCASE 3: DUP BOLD limbo"
                    echo -e "\t$BOLDJSON"
                    echo -e "\t* $BOLDJSON: $DUPJSON limbo BOLD NOR DUP matches expected TR" >> "$error_log"
                fi
                echo "\nCASE 4: No clue"
                echo "$BOLDJSON"
            fi
            break
        fi
    done           
    if [[ $found_match -eq 0 ]]; then
        echo "No matching key found in the array for $DUPJSON"
    fi
done 
