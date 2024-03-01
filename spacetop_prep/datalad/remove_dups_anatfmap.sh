# Define a file to log errors
error_log="error_log_funcanat.txt"

# mapfile -t dup_files < <(find . -type f -name '*__dup-*')

dup_files=()
while IFS= read -r -d $'\n' file; do
    dup_files+=("$file")
done < <(find . -type f -name '*fmap__dup-*')
# done < <(find . -type f -path '*/func/*__dup-*')
# Loop through each file found.
for DUPJSON in "${dup_files[@]}"; do
    # Use jq to extract TR values.
    DUPJSON_TR=$(jq '.dcmmeta_shape[3]' "${DUPJSON}")
    BOLDJSON=$(echo "${DUPJSON}" | sed 's/__dup-[0-9]*//')
    BOLDJSON_TR=$(jq '.dcmmeta_shape[3]' "${BOLDJSON}")
    if [[ "$BOLDJSON_TR" == "null" || "$BOLDJSON_TR" =~ "error" ]]; then
        echo "$BOLDJSON: Error extracting TR value." >> "$error_log"
        continue
    fi
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
            if [[ "$BOLDJSON_TR" -eq "$EXPECTED_TR" && "$DUPJSON_TR" -lt "$BOLDJSON_TR" ]]; then
                echo "Conditions met for $DUPJSON. Removing file."
                # Uncomment the next line to perform file removal
                
                # generic_filename=$(echo "$DUPJSON" | sed -E 's/(run-[0-9]+_).+(__dup-.+)/\1*\2/')
            generic_filename=$(echo "$DUPJSON" | sed -E 's/(run-[0-9]+_).+(__dup-[0-9]+).*/\1*\2.*/')
            read -a files_to_remove <<< "$generic_filename"

            # Loop through the array and remove each file
            for rm_file in "${files_to_remove[@]}"; do
                git rm "$rm_file"
            done

            else
                # Handle errors
                if [[ "$DUPJSON_TR" -ge "$BOLDJSON_TR" ]]; then
                    echo "$DUPJSON: DUPJSON_TR (${DUPJSON_TR}) is not smaller than BOLDJSON_TR (${BOLDJSON_TR})." >> "$error_log"
                fi
                if [[ "$BOLDJSON_TR" -ne "$EXPECTED_TR" ]]; then
                    echo "$BOLDJSON: BOLDJSON_TR (${BOLDJSON_TR}) does not match EXPECTED_TR ($EXPECTED_TR)." >> "$error_log"
                fi
            fi
            break
        fi
        done           
    if [[ $found_match -eq 0 ]]; then
        echo "No matching key found in the array for $DUPJSON"
    fi
done 
