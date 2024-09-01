function s03_sub_0001_task_alignvideo()
% Define the run ranges and maximum rows per run
run_ranges = {1:4, 5:8, 9:12, 13:14};
max_rows_per_run = [4, 4, 4, 2];  % Specify the number of rows for each run

% Define the list of video filenames corresponding to the runs
param_video_filename_list = {
    'ses-01_run-01_order-01_content-idiots.mp4',
    'ses-01_run-01_order-02_content-wanderers.mp4',
    'ses-01_run-01_order-03_content-lioncubs.mp4',
    'ses-01_run-01_order-04_content-parkour.mp4',
    'ses-01_run-02_order-01_content-harrymetsally.mp4',
    'ses-01_run-02_order-02_content-HB.mp4',
    'ses-01_run-02_order-03_content-islamophobia.mp4',
    'ses-01_run-02_order-04_content-beachsunset.mp4',
    'ses-01_run-03_order-01_content-huggingpets.mp4',
    'ses-01_run-03_order-02_content-bestfriendsweating.mp4',
    'ses-01_run-03_order-03_content-cupstacking.mp4',
    'ses-01_run-03_order-04_content-dancewithdeath.mp4',
    'ses-01_run-04_order-01_content-beatbox.mp4',
    'ses-01_run-04_order-02_content-angrygrandpa.mp4'
    };

% Loop over each run number
for run_num = 1:4
    % Select the relevant filenames for this run
    filename_range = run_ranges{run_num};
    selected_filenames = param_video_filename_list(filename_range)';
    
    % Load the corresponding data file
    file_path = sprintf('/Users/h/Documents/projects_local/1076_spacetop/sourcedata/d_beh/sub-0001/task-alignvideos/ses-01/sub-0001_ses-01_task-alignvideos_run-%02d_beh.mat', run_num);
    load(file_path)
    
    % initialize values by getting correct dataframe size
    selected_range = run_ranges{run_num};
    num_items = numel(explog.rating.times{selected_range(1)});
    rating_onset = zeros(numel(selected_range), num_items);
    rating_value = zeros(numel(selected_range), num_items);
    rating_RT = zeros(numel(selected_range), num_items);
    biopac_displayonset = NaN(numel(selected_range), num_items);
    biopac_response = NaN(numel(selected_range), num_items);
    
    for i = 1:num_items
        for j = 1:numel(selected_range)
            rating_onset(j, i) = explog.rating.times{selected_range(j)}(i);
            rating_value(j, i) = explog.rating.ratings{selected_range(j)}(i);
            rating_RT(j, i) = explog.rating.RT{selected_range(j)}(i);
        end
    end
    
    % Number of rows for this run
    num_rows = max_rows_per_run(run_num);
    
    % Create the table dynamically without padding
    T = table();
    % Assuming rating_onset, rating_value, and rating_RT are already defined as 4x7 matrices
    num_items = size(rating_onset, 2); % Number of items (7 in your case)
    num_rows = size(rating_onset, 1); % Number of rows (4 in your case)
    
    % Initialize the cell array for column names
    col_names = cell(1, num_items * 5);
    
    % Populate the column names
    for i = 1:num_items
        col_names{i} = sprintf('event02_rating0%d_displayonset', i);
        col_names{num_items + i} = sprintf('event02_rating0%d_rating', i);
        col_names{2*num_items + i} = sprintf('event02_rating0%d_RT', i);
        col_names{3*num_items + i} = sprintf('event02_rating0%d_biopac_displayonset', i);
        col_names{4*num_items + i} = sprintf('event02_rating0%d_biopac_response', i);
    end
    % Concatenate the data into one matrix in the correct order
    data_matrix = [rating_onset, rating_value, rating_RT, biopac_displayonset, biopac_response];
    
    % Convert the matrix to a table
    T = array2table(data_matrix, 'VariableNames', col_names);
    
    %% combine the rating dataframe with another dataframe with parameter and video onset data
    src_subject_id = repmat(1, num_rows, 1);
    session_id = repmat(1, num_rows, 1);
    param_run_num = repmat(run_num, num_rows, 1);
    param_trigger_onset = repmat(explog.param_trigger_onset(run_num), num_rows, 1);
    param_start_biopac = NaN(num_rows, 1);
    param_video_filename = selected_filenames';
    
    % Derive event01_video_onset and event01_video_end
    event01_video_onset = NaN(num_rows, 1);
    event01_video_end = NaN(num_rows, 1);
    range_idx = run_ranges{run_num};
    event01_video_onset(1:numel(range_idx)) = explog.movie_start(range_idx);
    event01_video_end(1:numel(range_idx)) = explog.movie_end(range_idx);
    event01_video_biopac = NaN(num_rows, 1);
    
    % Create the new columns table
    new_columns = table(src_subject_id, session_id, param_run_num, param_trigger_onset, ...
        param_start_biopac, param_video_filename, event01_video_onset, event01_video_biopac, event01_video_end);
    
    % Ensure that the new_columns and T have the same number of rows before concatenating
    if size(new_columns, 1) == size(T, 1)
        combinedT = [new_columns T];
    else
        error('Row mismatch between new_columns and T for run %d', run_num);
    end
    
    new_order = {'src_subject_id','session_id','param_run_num','param_trigger_onset','param_start_biopac','param_video_filename','event01_video_onset','event01_video_biopac','event01_video_end','event02_rating01_displayonset','event02_rating02_displayonset','event02_rating03_displayonset'	'event02_rating04_displayonset','event02_rating05_displayonset','event02_rating06_displayonset','event02_rating07_displayonset','event02_rating01_rating','event02_rating02_rating','event02_rating03_rating','event02_rating04_rating','event02_rating05_rating','event02_rating06_rating','event02_rating07_rating','event02_rating01_RT','event02_rating02_RT','event02_rating03_RT','event02_rating04_RT','event02_rating05_RT','event02_rating06_RT','event02_rating07_RT','event02_rating01_biopac_displayonset','event02_rating02_biopac_displayonset','event02_rating03_biopac_displayonset','event02_rating04_biopac_displayonset',	'event02_rating05_biopac_displayonset','event02_rating06_biopac_displayonset',	'event02_rating07_biopac_displayonset','event02_rating01_biopac_response','event02_rating02_biopac_response','event02_rating03_biopac_response','event02_rating04_biopac_response','event02_rating05_biopac_response','event02_rating06_biopac_response',	'event02_rating07_biopac_response'};
    T_reordered = combinedT(:, new_order);
    % Save the table to a file
    filename = sprintf('/Users/h/Documents/projects_local/1076_spacetop/sourcedata/d_beh/sub-0001/task-alignvideos/ses-01/sub-0001_ses-01_task-alignvideos_run-%02d_beh.csv', run_num);
    writetable(T_reordered, filename);
end
end
%%%%%%%
