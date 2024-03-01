% Preprocessing of behavior data from task-shortvideos

% This script extracts the moment-by-moment mouse position data (sampled at 
% 60 Hz) from original .mat files, finds ratings and motion time from them,
% and adds those data to original .csv files which contain all other time 
% stamps.
% The new .csv files will be named as *_beh_preproc.csv.

% See README.md and the associated paper (Jung et al., 2024) for more
% information.

clear

taskname = 'task-shortvideos';
>>>
% fill in the top level of your d_beh folder
dataDir = '';
>>>
% change below if you would like to process data from a subset of all subjects
endSub = 133;

for i = 1:endSub
    sub = strcat('sub-', sprintf("%04d", i));
    
    % .csv files contain onset time, stim_file, condition, etc.
    csvFile = fullfile(dataDir, sub, taskname, ...
        strcat(sub, '_ses-03_', taskname, '_beh.csv'));
    if ~exist(csvFile, 'file')
       continue
    end
    csvData = readtable(csvFile);

    % *trajectory.mat files contain mouse trajectories
    matFile = fullfile(dataDir, sub, taskname, ...
        strcat(sub, '_ses-03_', taskname, '_trajectory.mat'));
    if ~exist(matFile, 'file')
       % if there is .csv file but no .mat file
       % no information can be provided or updated
       continue
    end
    load(matFile)
    
    trialNum = size(csvData, 1);       % how many trials
    [rating_end_x, rating_end_y, RT_adj, motion_onset, motion_dur] ...
        = deal(zeros(trialNum, 1));    % data to extract and store

    for j = 1:trialNum
        traj = rating_trajectory{j};
        if ~isnan(csvData.event03_rating_RT(j))
            % subject made a response in this trial
            rating_end_x(j) = traj(end, 1);
            rating_end_y(j) = traj(end, 2);
            RT_adj(j) = NaN;
        else
            % there was no response in this trial
            % infer RT_adjusted by finding the last time mouse position changed
            % but keep RT as nan
            % disp(['Trial ' num2str(j) ' had no response'])  % for test
            for l = size(traj, 1):-1:2
                if (traj(l,1)~=traj(l-1,1)) || (traj(l,2)~=traj(l-1,2))
                    break
                end
            end
            if l == 2 && (traj(2,1) == traj(1,1))...
                            && (traj(2,2) == traj(1,2))
                % No movement at all
                RT_adj(j) = NaN;
                rating_end_x(j) = NaN;
                rating_end_y(j) = NaN;
            else
                % l-1 is when the last movement happened
                RT_adj(j) = (l-1)/60;
                rating_end_x(j) = traj(l, 1);
                rating_end_y(j) = traj(l, 2);
            end
        end    

        % find motion onset time and duration
        for l = 2:size(traj, 1)
            if (traj(l,1)~=traj(l-1,1)) || (traj(l,2)~=traj(l-1,2))
                break
            end
        end
        if traj(l,1) == traj(1,1) && traj(l,2) == traj(1,2)
            % mouse didn't move at all
            motion_onset(j) = NaN;
        else
            % l is when movement started
            motion_onset(j) = l/60;
        end
        if isnan(csvData.event03_rating_RT(j))
            % no response
            motion_dur(j) = RT_adj(j) - motion_onset(j);
        else
            motion_dur(j) = csvData.event03_rating_RT(j) - motion_onset(j);
        end
    end
    newCsvData = addvars(csvData, rating_end_x, rating_end_y, RT_adj, ...
        motion_onset, motion_dur, 'NewVariableNames', ...
        {'rating_end_x', 'rating_end_y', 'RT_adj', 'motion_onset', 'motion_dur'});
    outputFile = fullfile(dataDir, sub, taskname, ...
        strcat(sub, '_ses-03_', taskname, '_beh-preproc.csv'));
    writetable(newCsvData, outputFile)
    % if mod(i, 10)==0; disp(['sub-' num2str(i) ' done']); end    % for test
end