% Preprocessing of behavior data from task-shortvideos

% This script extracts the moment-by-moment mouse position data (sampled at
% 60 Hz) from original .mat files, finds ratings and motion time from them,
% and adds those data to original .csv files which contain all other time
% stamps.
% The new .csv files will be named as *_beh_preproc.csv.

% See README.md and the associated paper (Jung et al., 2024) for more
% information.

% check if the extracted degrees agree with the logged degrees

clear

taskname = 'task-social';
newtaskname = 'task-cue';
% >>>
% fill in the top level of your d_beh folder
dataDir = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata/d_beh';
% >>>
% change below if you would like to process data from a subset of all subjects
endSub = 133;

subjectDirs = dir(fullfile(dataDir, 'sub-*')); % List all directories that match 'sub-*'
subjectsWithTaskSocial = {}; % Initialize an empty cell array to hold subjects with 'task-social'

for k = 1:length(subjectDirs)
    if subjectDirs(k).isdir
        % Check if 'task-social' directory exists within the subject directory
        taskSocialDir = fullfile(dataDir, subjectDirs(k).name, 'task-social');
        if exist(taskSocialDir, 'dir')
            % If 'task-social' directory exists, add the subject directory to the list
            subjectsWithTaskSocial{end+1} = subjectDirs(k).name;
        end
    end
end

disp(subjectsWithTaskSocial);
for i = 2:length(subjectsWithTaskSocial)
    % for i = 1:endSub
    sub = subjectsWithTaskSocial{i};
    disp(sub);
    % sub = strcat('sub-', sprintf("%04d", i));
    sub_files = dir(fullfile(dataDir, sub, 'task-social','*', '*_beh.csv'));
    % for globbedfile
    %     % .csv files contain onset time, stim_file, condition, etc.
    %     csvFile = fullfile(dataDir, sub, taskname, ...
    %         strcat(sub, '_*_', taskname, '_beh.csv'));
    %     if ~exist(csvFile, 'file')
    %         continue
    %     end
    for file_ind = 1:length(sub_files)
        % Regular expression to match sub, ses, and run
        pattern = 'sub-(?<sub>\d{4})_ses-(?<ses>\d{2})_task-social_run-(?<run>\d{2})-(?<runtype>\w+)_beh\.csv';
        
        % Use regexp to search for patterns and extract matches
        matches = regexp(sub_files(file_ind).name, pattern, 'names');
        
        % Extract metadata from matches
        if ~isempty(matches)
            sub = ['sub-', matches.sub];
            ses = ['ses-', matches.ses];
            run = ['run-', matches.run];
            runtype = ['runtype-', matches.runtype];
            
            % Display extracted metadata
            fprintf('sub: %s\n', sub);
            fprintf('ses: %s\n', ses);
            fprintf('run: %s\n', run);
        else
            disp('No matches found.');
            continue
        end
        
        %% load data
        % *outcome_trajectory.mat files contain mouse outcome_trajectories
        matFile = dir(fullfile(dataDir, sub, taskname, ses,...
            strcat(sub, '_', ses, '_', taskname, '_', run, '*_trajectory.mat')));
        csvFile = dir(fullfile(dataDir, sub, taskname, ses,...
            strcat(sub, '_', ses, '_', taskname, '_', run, '*_beh.csv')));
        
        if isempty(matFile)
            disp('sub exists but no trajectory file');
            continue;
        end
        matfile_fname = fullfile(matFile.folder, matFile.name);
        % if ~exist(matfile_fname, 'file')
        %     % if there is .csv file but no .mat file
        %     % no information can be provided or updated
        %     disp('sub exists but no trajectory file')
        %     continue
        % end
        % load behavioral and outcome_trajectory data __________________________
        % the early participants had a matfile with rating_trajectory, vs some other had rating_Trajectory
        dataStruct = load(matfile_fname);
        % Check for the existence of the variables and assign to a standard name
        if isfield(dataStruct, 'rating_Trajectory')
            rating_Trajectory = dataStruct.rating_Trajectory;
            disp(strcat(sub, ' rating_Trajectory'))
        elseif isfield(dataStruct, 'rating_trajectory')
            rating_Trajectory = dataStruct.rating_trajectory;
            disp(strcat(sub, ' rating_trajectory'))
        else
            error('Required variable not found in the .mat file.');
        end
        csvData = readtable(fullfile(csvFile.folder, csvFile.name));
        
        
        trialNum = size(csvData, 1);       % how many trials
        [expectrating_end_x, expectrating_end_y,expectRT_adj, expect_motiononset,expect_motiondur,            outcomerating_end_x, outcomerating_end_y, outcomeRT_adj, outcome_motiononset, outcome_motiondur,] ...
            = deal(zeros(trialNum, 1));    % data to extract and store
        
        %% trajectory
        for j = 1:trialNum
            outcome_traj = rating_Trajectory{j, 2};
            if ismember('event04_actual_RT', csvData.Properties.VariableNames)
                % if ~isnan(csvData.event03_rating_RT(j))
                if ~isnan(csvData.event04_actual_RT(j))
                    % subject made a response in this trial
                    outcomerating_end_x(j) = outcome_traj(end,1);
                    outcomerating_end_y(j) = outcome_traj(end,2);
                    outcomeRT_adj(j) = NaN;
                else
                    % there was no response in this trial
                    % infer RT_adjusted by finding the last time mouse position changed
                    % but keep RT as nan
                    % disp(['Trial ' num2str(j) ' had no response'])  % for test
                    for l = size(outcome_traj, 1):-1:2
                        if (outcome_traj(l,1)~=outcome_traj(l-1,1)) || (outcome_traj(l,2)~=outcome_traj(l-1,2))
                            break
                        end
                    end
                    if l == 2 && (outcome_traj(2,1) == outcome_traj(1,1))...
                            && (outcome_traj(2,2) == outcome_traj(1,2))
                        % No movement at all
                        outcomeRT_adj(j) = NaN;
                        outcomerating_end_x(j) = NaN;
                        outcomerating_end_y(j) = NaN;
                    else
                        % l-1 is when the last movement happened
                        outcomeRT_adj(j) = (l-1)/60;
                        outcomerating_end_x(j) = outcome_traj(l, 1);
                        outcomerating_end_y(j) = outcome_traj(l, 2);
                    end
                end
                
                % find motion onset time and duration
                for l = 2:size(outcome_traj, 1)
                    if (outcome_traj(l,1)~=outcome_traj(l-1,1)) || (outcome_traj(l,2)~=outcome_traj(l-1,2))
                        break
                    end
                end
                if outcome_traj(l,1) == outcome_traj(1,1) && outcome_traj(l,2) == outcome_traj(1,2)
                    % mouse didn't move at all
                    outcome_motiononset(j) = NaN;
                else
                    % l is when movement started
                    outcome_motiononset(j) = l/60;
                end
                if isnan(csvData.event04_actual_RT(j))
                    % no response
                    outcome_motiondur(j) = outcomeRT_adj(j) - outcome_motiononset(j);
                else
                    outcome_motiondur(j) = csvData.event04_actual_RT(j) - outcome_motiononset(j);
                end
            else
                % Handle cases where the 'event04_actual_RT' column does not exist
                warning('Variable "event04_actual_RT" not found in CSV file for trial %d. Skipping this trial.', j);
                outcomerating_end_x(j) = NaN;
                outcomerating_end_y(j) = NaN;
                outcomeRT_adj(j) = NaN;
                outcome_motiononset(j) = NaN;
                outcome_motiondur(j) = NaN;
            end
        end
        
        
        for j = 1:trialNum
            expect_traj = rating_Trajectory{j,1};
            
            if ismember('event02_actual_RT', csvData.Properties.VariableNames)
                if ~isnan(csvData.event02_expect_RT(j))
                    % subject made a response in this trial
                    expectrating_end_x(j) = expect_traj(end, 1);
                    expectrating_end_y(j) = expect_traj(end, 2);
                    expectRT_adj(j) = NaN;
                else
                    % there was no response in this trial
                    % infer RT_adjusted by finding the last time mouse position changed
                    % but keep RT as nan
                    % disp(['Trial ' num2str(j) ' had no response'])  % for test
                    for l = size(expect_traj, 1):-1:2
                        if (expect_traj(l,1)~=expect_traj(l-1,1)) || (expect_traj(l,2)~=expect_traj(l-1,2))
                            break
                        end
                    end
                    if l == 2 && (expect_traj(2,1) == expect_traj(1,1))...
                            && (expect_traj(2,2) == expect_traj(1,2))
                        % No movement at all
                        expectRT_adj(j) = NaN;
                        expectrating_end_x(j) = NaN;
                        expectrating_end_y(j) = NaN;
                    else
                        % l-1 is when the last movement happened
                        expectRT_adj(j) = (l-1)/60;
                        expectrating_end_x(j) = expect_traj(l, 1);
                        expectrating_end_y(j) = expect_traj(l, 2);
                    end
                end
                
                % find motion onset time and duration
                for l = 2:size(expect_traj, 1)
                    if (expect_traj(l,1)~=expect_traj(l-1,1)) || (expect_traj(l,2)~=expect_traj(l-1,2))
                        break
                    end
                end
                if expect_traj(l,1) == expect_traj(1,1) && expect_traj(l,2) == expect_traj(1,2)
                    % mouse didn't move at all
                    expect_motiononset(j) = NaN;
                else
                    % l is when movement started
                    expect_motiononset(j) = l/60;
                end
                if isnan(csvData.event02_expect_RT(j))
                    % no response
                    expect_motiondur(j) = expectRT_adj(j) - expect_motiondur(j);
                else
                    expect_motiondur(j) = csvData.event02_expect_RT(j) - expect_motiononset(j);
                end
                
            else
                warning('Variable "event02_expect_RT" not found in CSV file for trial %d. Skipping this trial.', j);
                expectrating_end_x(j) = NaN;
                expectrating_end_y(j) = NaN;
                expectRT_adj(j) = NaN;
                expect_motiononset(j) = NaN;
                expect_motiondur(j) = NaN;
            end
        end
        
        
        
        newCsvData = addvars(csvData, expectrating_end_x, expectrating_end_y,expectRT_adj, expect_motiononset,expect_motiondur,            outcomerating_end_x, outcomerating_end_y, outcomeRT_adj, outcome_motiononset, outcome_motiondur, 'NewVariableNames', ...
            {'expectrating_end_x', 'expectrating_end_y','expectRT_adj',...
            'expect_motiononset','expect_motiondur',...
            'outcomerating_end_x', 'outcomerating_end_y', 'outcomeRT_adj', 'outcome_motiononset', 'outcome_motiondur'});
        save_dir = fullfile(dataDir, sub, newtaskname, ses);
        if ~exist(save_dir, 'dir')
            mkdir(save_dir);
        end
        outputFile = fullfile(save_dir,...
            strcat(sub, '_', ses, '_', newtaskname, '_', run, '_', runtype,'_beh-preproc.csv'));
        writetable(newCsvData, outputFile)
        
    end
end
