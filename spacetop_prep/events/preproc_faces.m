% Preprocessing of behavior data from task-faces

% This script extracts the moment-by-moment mouse position data (sampled at 
% 60 Hz) from original .mat files, finds ratings and motion time from them,
% and adds those data to original .csv files which contain all other time 
% stamps.
% The new .csv files will be named as *_beh_preproc.csv.

% See README.md and the associated paper (Jung et al., 2024) for more
% information.

clear

taskname = 'task-faces';
>>>
% fill in the top level of your d_beh folder
dataDir = '';
>>>
% change below if you would like to process data from a subset of all subjects
endSub = 133;

blockCond = {{'age', 'sex', 'intensity'}, ...
    {'intensity', 'sex', 'age'}};    % two block orders for subjects with even and odd IDs

for i = 1:endSub
    sub = strcat('sub-', sprintf("%04d", i));
    blocks = blockCond{rem(i, 2)+1};

    for r = 1:3    % three runs per subject
        judgment = blocks{r};    % the type of judgments in this run

        % .csv files contain onset time, stim_file, condition, etc.
        csvFile = fullfile(dataDir, sub, taskname, ...
            strcat(sub, '_ses-02_', taskname, '_run-0', num2str(r), ...
            '-', judgment, '_beh.csv'));
        if ~exist(csvFile, 'file')
           continue
        end
        csvData = readtable(csvFile);
    
        % *trajectory.mat files contain mouse trajectories
        matFile = fullfile(dataDir, sub, taskname, ...
            strcat(sub, '_ses-02_', taskname, '_run-0', num2str(r), ...
            '-', judgment, '_beh_trajectory.mat'));
        if ~exist(matFile, 'file')
           % if there is .csv file but no .mat file
           % no information can be provided or updated
           continue
        end
        load(matFile)
        
        trialNum = size(csvData, 1);    % how many trials
        [rating_end_x, rating_converted, RT_adj, motion_onset, motion_dur] ...
            = deal(zeros(trialNum, 1));    % new data to extract and store
    
        for j = 1:trialNum
            traj = rating_Trajectory{j, 2};
            RT = csvData.event03_rating_RT(j);
            if ~isnan(RT)
                % there was response in this trial
                if RT < 1.375 && floor(RT*60) <= size(traj, 1)
                    rating_end_x(j) = traj(floor(RT*60), 1);
                        % the rating should be when the mouse was clicked
                        % not the last one in the trajectory (extra 0.5 seconds
                        % of recording)
                else
                    rating_end_x(j) = traj(end, 1);
                end
                rating_converted(j) = (rating_end_x(j)-729.6)/(1224-729.6);
                    % convert all ratings to [0, 1]
                    % the max and min values of x are 1224 and 729.6
                RT_adj(j) = NaN;
            else
                % there was no response in this trial
                % infer RT_adjusted by finding the last time mouse position changed
                % but keep RT as nan
                % disp(['Trial ' num2str(j) ' had no response'])  % for test
                if size(traj, 1) == 1
                    % there is only one recording in this trial, nothing
                    % can be imputed
                    RT_adj(j) = NaN;
                    rating_end_x(j) = NaN;
                    rating_converted(j) = NaN;
                    motion_onset(j) = NaN;
                    motion_duration(j) = NaN;
                    continue
                end

                for l = size(traj, 1):-1:2
                    if (traj(l,1)~=traj(l-1,1))
                        break
                    end
                end
                if l == 2 && (traj(2,1) == traj(1,1))
                    % No movement at all
                    RT_adj(j) = NaN;
                    rating_end_x(j) = NaN;
                    rating_converted(j) = NaN;
                else
                    % l-1 is when the last movement happened
                    RT_adj(j) = (l-1)/60;
                    rating_end_x(j) = traj(l, 1);
                    rating_converted(j) = (rating_end_x(j)-729.6)/(1224-729.6);
                end
            end    
    
            % find motion onset time and duration
            for l = 2:size(traj, 1)
                if (traj(l,1)~=traj(l-1,1))
                    break
                end
            end
            if traj(l,1) == traj(1,1)
                % mouse didn't move at all
                motion_onset(j) = NaN;
            else
                motion_onset(j) = l/60;
            end
            if isnan(RT)
                % no response
                motion_dur(j) = RT_adj(j) - motion_onset(j);
            else
                motion_dur(j) = RT - motion_onset(j);
            end
        end
        newCsvData = addvars(csvData, rating_end_x, rating_converted, RT_adj, ...
            motion_onset, motion_dur, 'NewVariableNames', ...
            {'rating_end_x', 'rating_converted', 'RT_adj', 'motion_onset', 'motion_dur'});
        outputFile = fullfile(dataDir, sub, taskname, ...
            strcat(sub, '_ses-02_', taskname, '_run-0', num2str(r), ...
            '-', judgment, '_beh-preproc.csv'));
        writetable(newCsvData, outputFile)
    end
    % if mod(i, 10)==0; disp(['sub-' num2str(i) ' done']); end   % for test
end
