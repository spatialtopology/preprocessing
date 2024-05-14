#NEED TO REMOVE PRIMARY and rename DUP as PRIMARY
# PRIMARYJSON="sub-0122_ses-03_acq-mb8_dir-ap_run-01_epi.json"
DUPJSON="./sub-0122/ses-03/fmapsub-0122_ses-03_acq-mb8_dir-ap_run-01_epi__dup-01.json"
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

if [ "$PRIMARYJSON_SEC" -lt "$DUPJSON_SEC" ]; then
echo -e "\n${DUPJSON}\nPRIMARYJSON acquisition time is earlier." >> $LOG_FILE
     # echo -e "\n>>>>> ERROR: PRIMARYJSON ${PRIMARYJSON_NODEC} ${PRIMARYJSON_SEC} has an earlier time than DUPJSON ${DUPJSON_NODEC} ${DUPJSON_SEC}\n\n" >> $LOG_FILE

     # SWAP DUP AND PRIMARY, THEN DELETED
     PRIMARYGZ=${PRIMARYJSON}
     DUPGZ=${DUPJSON} #TODO remove file extension
     # RENAME JSON primary is crap, keep dup
     $(dirname "$0")/rename_file "${PRIMARYJSON}" CRAPJSON; 
     $(dirname "$0")/rename_file "${DUPJSON}" "${PRIMARYJSON}"; 
     $(dirname "$0")/rename_file CRAPJSON "${DUPJSON}"
     # # RENAME fmap
     $(dirname "$0")/rename_file "${PRIMARYGZ}" CRAPNII; 
     $(dirname "$0")/rename_file "${DUPGZ}" "${PRIMARYGZ}"; 
     $(dirname "$0")/rename_file CRAPNII "${DUPGZ}"
     # DELETE files
     git rm "${DUPGZ}"
     git rm "${DUPJSON}"

fi