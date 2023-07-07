#!/bin/bash -l
#SBATCH --job-name=physio
#SBATCH --nodes=1
#SBATCH --task=4
#SBATCH --mem-per-cpu=100gb
#SBATCH --time=01:30:00
#SBATCH -o ./log/physio03_%A_%a.o
#SBATCH -e ./log/physio03_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1
###%-14%5

conda activate biopac
PROJECT_DIR="/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_cue"

# Define the YAML configuration file
CONFIGFILE="p01_config.yaml"

# Read the YAML configuration file using yq and store the values in variables
while IFS=":" read -r key value; do
  var_name=$(echo "$key" | tr -d '[:space:]' | tr '-' '_')
  var_value=$(echo "$value" | tr -d '[:space:]')
  eval "$var_name=\"$var_value\""
done < <(yq eval '.[] | to_entries | .[] | .key + ":" + (.value | tostring)' "${CONFIGFILE}")

# Run the Python script with the extracted parameter values
python ${PWD}/p01_grouplevel_01SCL.py \
--input-physiodir "$input_physiodir" \
--input-behdir "$input_behdir" \
--output-logdir "$output_logdir" \
--output-savedir "$output_savedir" \
--metadata "$metadata" \
--dictchannel "$dictchannel" \
--slurm-id "$slurm_id" \
--slurm-stride "$slurm_stride" \
--bids-zeropad "$bids_zeropad" \
--bids-task "$bids_task" \
--event-name "$event_name" \
--prior-event "$prior_event" \
--later-event "$later_event" \
--source-samplingrate "$source_samplingrate" \
--dest-samplingrate "$dest_samplingrate" \
--scl-epochstart "$scl_epochstart" \
--scl-epochend "$scl_epochend" \
--ttl-index "$ttl_index" \
--baselinecorrect "$baselinecorrect" \
--exclude-sub ${exclude_sub//,/ }