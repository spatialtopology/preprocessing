"""
This code identifies sub/ses/task/run files that have shorter than expected TRs

"""
import json
import os, glob

# Standard values based on the task and run combination
standard_values = {
    "task-narratives_acq-mb8_run-01": 967,
    "task-narratives_acq-mb8_run-02": 1098,
    "task-narratives_acq-mb8_run-03": 1298,
    "task-narratives_acq-mb8_run-04": 1156,
    "task-social": 872,
    "task-fractional_acq-mb8_run-01": 1322,
    "task-fractional_acq-mb8_run-02": 1322,
    "task-shortvideo": 1616,
    "task-faces": 914,
    "ses-01_task-alignvideo_acq-mb8_run-01": 1073,
    "ses-01_task-alignvideo_acq-mb8_run-02": 1376,
    "ses-01_task-alignvideo_acq-mb8_run-03": 1016,
    "ses-01_task-alignvideo_acq-mb8_run-04": 1209,
    "ses-02_task-alignvideo_acq-mb8_run-01": 839,
    "ses-02_task-alignvideo_acq-mb8_run-02": 1859,
    "ses-02_task-alignvideo_acq-mb8_run-03": 1158,
    "ses-02_task-alignvideo_acq-mb8_run-04": 914,
    "ses-03_task-alignvideo_acq-mb8_run-01": 1157,
    "ses-03_task-alignvideo_acq-mb8_run-02": 1335,
    "ses-03_task-alignvideo_acq-mb8_run-03": 1065,
    "ses-04_task-alignvideo_acq-mb8_run-01": 1268,
    "ses-04_task-alignvideo_acq-mb8_run-02": 926,
}

def check_dcmmeta_shape(file_path, task_run_combination):
    # Read the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Extract the fourth value from 'dcmmeta_shape'
    dcmmeta_shape = data.get("dcmmeta_shape", [])
    if len(dcmmeta_shape) == 4:
        tr_value = dcmmeta_shape[3]
        # Compare against the standard
        if task_run_combination in standard_values:
            if tr_value < standard_values[task_run_combination]:
                return True, tr_value
    return False, None

# Directory where your JSON files are located
json_dir = '/Users/h/Documents/projects_local/1076_spacetop'

json_files = sorted(glob.glob(os.path.join(json_dir, 'sub-*/ses-*/func/*_bold.json')))

# Loop through the found files and check each one
for file_path in json_files:
    filename = os.path.basename(file_path)
    
    # Parse out sub, ses, task, run from the filename
    parts = filename.split('_')
    sub = parts[0]
    ses = parts[1]
    task = parts[2] + "_" + parts[3] if "acq" in parts[3] else parts[2]
    run = parts[4]
    task_run_combination = f"{task}_{run.replace('.json', '')}"
    
    # Full path to the JSON file
    file_path = os.path.join(json_dir, sub, ses, 'func', filename)
    
    # Check the JSON file and get the result
    is_shorter, tr_value = check_dcmmeta_shape(file_path, task_run_combination)
    if is_shorter:
        print(f"{filename} has a dcmmeta_shape shorter than the standard. Value: {tr_value}")
