import re
import pandas as pd
from pathlib import Path
import json
import subprocess

# Constants
DATALAD_DIR = Path('/Users/h/Documents/projects_local/1076_spacetop')
SCANNOTES_FNAME = Path('/Users/h/Documents/projects_local/cue_expectancy/resources/spacetop_scannotes/ST_Participants - scan_info_08-10-2022.csv')

# Task mapping dictionary
task_mapping = {
    'T1': 'task-t1',
    'DWI': 'task-dwi',
    'Fractional': 'task-fractional',
    'PVC': 'task-social',
    'short-video': 'task-shortvideo',
    'Narratives': 'task-narratives',
    'Faces': 'task-faces',
    'Align Videos': 'task-alignvideo'
}

def extract_task_run(column_name):
    """
    Extracts task and run information from a given column name.
    
    Parameters:
        column_name (str): The column name containing task and run information.
    
    Returns:
        dict: A dictionary containing the task and run extracted from the column name.
    """
    parts = column_name.split('\n')
    if len(parts) > 2:
        task_name = parts[1].strip()
        run_name = parts[2].strip().lower()
        task = task_mapping.get(task_name, 'unknown-task')
        return {"task": task, "run": run_name}
    return {"task": "unknown-task", "run": "unknown-run"}

def TRmapper(result):
    """
    Maps the task and run combination to the corresponding TR value.
    
    Parameters:
        result (dict): A dictionary containing BIDS session, task, and run information.
    
    Returns:
        int: The TR value for the given task and run.
    
    Raises:
        KeyError: If the task and run combination is not found in the TRdict.
    """
    TRdict = {
        "task-narratives_acq-mb8_run-01": 967,
        "task-narratives_acq-mb8_run-02": 1098,
        "task-narratives_acq-mb8_run-03": 1298,
        "task-narratives_acq-mb8_run-04": 1156,
        "task-social": 872,
        "task-fractional_acq-mb8_run-01": 1323,
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
        "ses-04_task-alignvideo_acq-mb8_run-02": 926
    }
    bids_string = f"{result['BIDS_ses']}_{result['BIDS_task']}_acq-mb8_{result['BIDS_run']}"
    for key in TRdict.keys():
        if key in bids_string:
            return TRdict[key]
    raise KeyError(f"{bids_string} not found in TRdict")

def load_scan_notes(filename):
    """
    Loads the scan notes CSV file into a pandas DataFrame.
    
    Parameters:
        filename (str): The path to the scan notes CSV file.
    
    Returns:
        DataFrame: The loaded pandas DataFrame.
    """
    return pd.read_csv(filename)

def find_no_data_cells(df):
    """
    Finds cells in the DataFrame that match specific conditions and extracts relevant BIDS metadata.
    
    Parameters:
        df (DataFrame): The DataFrame containing scan notes.
    
    Returns:
        list: A sorted list of dictionaries with BIDS metadata for cells that match the conditions.
    """
    results = []
    for row in range(df.shape[0]):
        for col in range(df.shape[1]):
            cell_value = df.iat[row, col]
            if (cell_value == "no_data" or
                cell_value == "complete_dontuse" or
                cell_value == "repeat_dontuse"):
                bids_sub = df.at[row, "BIDS_id"]
                col_value = df.columns[col]
                bids_ses = df.at[row, "Session #"]
                scan_comments = df.at[row, "Scan comments?"]
                result = extract_task_run(col_value)
                bids_task = result['task']
                bids_run = result['run']
                results.append({
                    "BIDS_sub": bids_sub,
                    "Column": col_value,
                    "BIDS_task": bids_task,
                    "BIDS_run": bids_run,
                    "BIDS_ses": bids_ses,
                    "Scan_comments": scan_comments
                })
    return sorted(results, key=lambda x: x["BIDS_sub"])

def run_git_grep():
    """
    Runs a git grep command to find files containing 'TODO' and returns the list of files.
    
    Returns:
        list: A list of file paths containing 'TODO'.
    
    Raises:
        RuntimeError: If the git grep command fails.
    """
    process = subprocess.Popen(['git', 'grep', '-l', 'TODO'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"Error: {stderr.decode()}")
    return stdout.decode().splitlines()

def filter_todo_events(files):
    """
    Filters the list of files to include only those ending with '_events.tsv'.
    
    Parameters:
        files (list): The list of file paths.
    
    Returns:
        list: The filtered list of file paths.
    """
    return [file for file in files if Path(file).name.endswith('_events.tsv')]

def check_files_to_delete(result, todo_events_list):
    """
    Checks if files should be deleted based on BIDS metadata and specific conditions.
    
    Parameters:
        result (dict): A dictionary containing BIDS metadata.
        todo_events_list (list): A list of files containing 'TODO'.
    
    Returns:
        str: The action ('delete', 'investigate_intactevents', 'investigate_intactTR', 'investigate_nojson', or 'other').
        str: The BIDS string for the files.
        str: The scan comments for the files.
    """
    sub = result['BIDS_sub']
    ses = result['BIDS_ses']
    task = result['BIDS_task']
    run = result['BIDS_run']
    scan_comments = result['Scan_comments']
    bids_string = f"{sub}_{ses}_{task}_acq-mb8_{run}"
    bids_subdir = DATALAD_DIR / sub / ses / 'func'
    matching_files = sorted(list(bids_subdir.glob(bids_string + "*")))

    print(f"Matching files for {bids_string}: {matching_files}")

    found_relevant_file = False

    for file_path in matching_files:
        print(f"Processing file: {file_path}")

        if file_path.suffix == '.gz' and '_bold' in file_path.stem:
            found_relevant_file = True
            json_file_path = file_path.with_name(file_path.stem.split('.nii')[0] + '.json')
            print(f"Expected JSON file path: {json_file_path}")

            if json_file_path.exists():
                print(f"JSON file exists: {json_file_path}")
                with open(json_file_path, 'r') as json_file:
                    json_data = json.load(json_file)
                    TRlength = json_data.get('dcmmeta_shape', None)[-1]
                    expectedTR = TRmapper(result)
                    print(f"TR length: {TRlength}, Expected TR: {expectedTR}")

                    if TRlength and TRlength < expectedTR:
                        matching_filenames = [file.name for file in matching_files]
                        todo_intersect = [file for file in todo_events_list if any(file.endswith(match) for match in matching_filenames)]
                        print(f"todo_intersect: {todo_intersect}")

                        if todo_intersect:
                            return "delete", bids_string, scan_comments
                        else:
                            return "investigate_intactevents", bids_string, scan_comments
                    else:
                        return "investigate_intactTR", bids_string, scan_comments
            else:
                print(f"Missing JSON file for: {file_path}")
                return "investigate_nojson", bids_string, scan_comments

    if not found_relevant_file:
        print(f"No relevant files found for: {bids_string}")
    
    return "other", bids_string, scan_comments

def main():
    """
    Main function to process the scan notes and identify files to delete or investigate.
    """
    df = load_scan_notes(SCANNOTES_FNAME)
    sorted_results = find_no_data_cells(df)
    try:
        files = run_git_grep()
        todo_events_list = filter_todo_events(files)
    except RuntimeError as e:
        print(e)
        return

    # Lists to hold BIDS strings and comments
    deletelist = []
    investigate_intactevents = []
    investigate_intactTR = []
    investigate_nojson = []
    other = []

    for result in sorted_results:
        action, bids_string, scan_comments = check_files_to_delete(result, todo_events_list)
        if action == "delete":
            deletelist.append({"BIDS_string": bids_string, "Scan_comments": scan_comments})
        elif action == "investigate_intactevents":
            investigate_intactevents.append({"BIDS_string": bids_string, "Scan_comments": scan_comments})
        elif action == "investigate_intactTR":
            investigate_intactTR.append({"BIDS_string": bids_string, "Scan_comments": scan_comments})
        elif action == "investigate_nojson":
            investigate_nojson.append({"BIDS_string": bids_string, "Scan_comments": scan_comments})
        elif action == "other":
            other.append({"BIDS_string": bids_string, "Scan_comments": scan_comments})

    # Convert lists to DataFrames for easier display and manipulation
    df_delete = pd.DataFrame(deletelist)
    df_investigate_intactevents = pd.DataFrame(investigate_intactevents)
    df_investigate_intactTR = pd.DataFrame(investigate_intactTR)
    df_investigate_nojson = pd.DataFrame(investigate_nojson)
    df_other = pd.DataFrame(other)

    # Display the DataFrames
    print("Files to delete:")
    print(df_delete)
    print("\nFiles to investigate (intact events.tsv):")
    print(df_investigate_intactevents)
    print("\nFiles to investigate (intact TR):")
    print(df_investigate_intactTR)
    print("\nFiles to investigate (missing JSON):")
    print(df_investigate_nojson)
    print("\nOther files:")
    print(df_other)

    # Add the Deprecate_category column to each DataFrame
    df_delete['Deprecate_category'] = 'delete'
    df_investigate_intactevents['Deprecate_category'] = 'investigate: non empty events file'
    df_investigate_intactTR['Deprecate_category'] = 'investigate: TR length correct'
    df_investigate_nojson['Deprecate_category'] = 'investigate: no json'
    df_other['Deprecate_category'] = 'investigate: other'

    # Combine all DataFrames
    merged_df = pd.concat([df_delete, df_investigate_intactevents, df_investigate_intactTR, df_investigate_nojson, df_other], ignore_index=True)

    # Reorder the columns
    merged_df = merged_df[['Deprecate_category', 'BIDS_string', 'Scan_comments']]

    # Display the merged DataFrame
    print(merged_df)

    merged_df.to_csv(Path(DATALAD_DIR,'code','spacetop-prep','spacetop_prep','datalad','delete_bold.tsv'), index=False, sep='\t')

if __name__ == "__main__":
    main()
