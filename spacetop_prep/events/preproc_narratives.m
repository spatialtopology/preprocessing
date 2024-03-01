% Preprocessing of behavior data from task-narratives

% This script extracts the moment-by-moment mouse position data (sampled at 
% 60 Hz) from original .mat files, finds ratings and motion time from them,
% and adds those data to original .csv files which contain all other time 
% stamps. 
% The new .csv files will be named as *_beh_preproc.csv.

% See README.md and the associated paper (Jung et al., 2024) for more
% information.

clear

taskname = 'task-narratives';
>>>
% fill in the top level of your d_beh folder
dataDir = '';
>>>
% change below if you would like to process data from a subset of all subjects
endSub = 133;

>>>
% besides the `d_beh` repo, you will need another repo (task-narratives 
% [https://github.com/spatialtopology/task-narratives]) to get all the
% information needed to generate the events files
% clone it, then fill in the top level of your task_narratives folder 
taskDesignDir = '';
DesignTable = readtable(fullfile(dataDir, "design", "task-narratives_counterbalance_ver-01.csv"));
narratives = {[7, 8], [5, 6], [3, 4], [1, 2]};    % narrative presented in each run

for i = 1:endSub
    sub = strcat('sub-', sprintf("%04d", i));

    for r = 1:4    % four runs
        % .csv files contain onset time, stim_file, condition, etc.
        csvFile = fullfile(dataDir, sub, taskname, ...
            strcat(sub, '_ses-02_', taskname, '_run-0', num2str(r), '_beh.csv'));
        if ~exist(csvFile, 'file')
           continue
        end
        csvData = readtable(csvFile);

        % *trajectory.mat files contain mouse trajectories
        matFile = fullfile(dataDir, sub, taskname, ...
            strcat(sub, '_ses-02_', taskname, '_run-0', num2str(r), ...
            '_beh_trajectory.mat'));
        if ~exist(matFile, 'file')
           % if there is .csv file but no .mat file
           % no information can be provided or updated
           continue
        end
        load(matFile)
    
        trialNum = size(csvData, 1);    % how many trials
        [feeling_end_x, feeling_end_y, RT_feeling, RT_feeling_adj, motion_onset_feeling, ...
            motion_dur_feeling, expectation_end_x, expectation_end_y, ...
            RT_expectation, RT_expectation_adj, motion_onset_expectation, motion_dur_expectation] ...
            = deal(zeros(trialNum, 1));    % new data to extract and store
        [situation, context] = deal(cell(trialNum, 1));
    
        for k = 1:trialNum
            % Select the final rating point based on reaction time
                % Because of a feature in the experiment code, if the reaction
                % time is shorter than 3.5s, in the last 0.5 seconds the 
                % experiment program would still record mouse position
            
            % For feeling
            feelRT = csvData.event03_feel_RT(k);
            if ~isnan(feelRT)
                if feelRT <= 3.5
                    % sample an additional 0.5*60 = 30 times
                    feeling_end_x(k) = rating_Trajectory{k,1}(end-30,1);
                    feeling_end_y(k) = rating_Trajectory{k,1}(end-30,2);
                    RT_feeling(k) = feelRT;
                elseif feelRT > 3.5
                    % sample an additional (4-RT)*60 times
                    addsam = round((4-feelRT)*60);
                    feeling_end_x(k) = rating_Trajectory{k,1}(end-addsam,1);
                    feeling_end_y(k) = rating_Trajectory{k,1}(end-addsam,2);
                    RT_feeling(k) = feelRT;
                end
                RT_feeling_adj(k) = NaN;
            else
                % no recorded RT, impute the RT (RT_adj) by seeking the last "transition point"
                RT_feeling(k) = NaN;
                for l = size(rating_Trajectory{k,1},1):-1:2
                    if (rating_Trajectory{k,1}(l,1) ~= rating_Trajectory{k,1}(l-1,1))...
                            || (rating_Trajectory{k,1}(l,2) ~= rating_Trajectory{k,1}(l-1,2))
                        break
                    end
                end
                if l == 2 && (rating_Trajectory{k,1}(2,1) == rating_Trajectory{k,1}(1,1))...
                            && (rating_Trajectory{k,1}(2,2) == rating_Trajectory{k,1}(1,2))
                    % No movement at all
                    RT_feeling_adj(k) = NaN;
                    feeling_end_x(k) = NaN;
                    feeling_end_y(k) = NaN;
                else
                    % l-1 is when the last movement happened
                    RT_feeling_adj(k) = (l-1)/60;
                    feeling_end_x(k) = rating_Trajectory{k,1}(end,1);
                    feeling_end_y(k) = rating_Trajectory{k,1}(end,2);
                end
            end
            % find decision onset time
            for l = 2:size(rating_Trajectory{k,1}, 1)
                if (rating_Trajectory{k,1}(l,1) ~= rating_Trajectory{k,1}(l-1,1))...
                        || (rating_Trajectory{k,1}(l,2) ~= rating_Trajectory{k,1}(l-1,2))
                    break
                end
            end
            if rating_Trajectory{k,1}(l,1) == rating_Trajectory{k,1}(1,1) && ...
                        rating_Trajectory{k,1}(l,2) == rating_Trajectory{k,1}(1,2)
                        % mouse didn't move at all
                motion_onset_feeling(k) = NaN;
                motion_dur_feeling(k) = NaN;
            else
                motion_onset_feeling(k) = (l-1)/60;
                if isnan(feelRT)
                    % no response
                    motion_dur_feeling(k) = RT_feeling_adj(k) - motion_onset_feeling(k);
                else
                    motion_dur_feeling(k) = RT_feeling(k) - motion_onset_feeling(k);
                end
            end
            

            % For expectation
            expectRT = csvData.event04_expect_RT(k);
            if ~isnan(expectRT)
                RT_expectation_adj(k) = NaN;
                if expectRT <= 3.5
                    % sample an additional 0.5*60 = 30 times
                    expectation_end_x(k) = rating_Trajectory{k,2}(end-30,1);
                    expectation_end_y(k) = rating_Trajectory{k,2}(end-30,2);
                    RT_expectation(k) = expectRT;
                elseif expectRT > 3.5
                    % sample an additional (4-RT)*60 times
                    addsam = round((4-expectRT)*60);
                    expectation_end_x(k) = rating_Trajectory{k,2}(floor(end-addsam),1);
                    expectation_end_y(k) = rating_Trajectory{k,2}(floor(end-addsam),2);
                    RT_expectation(k) = expectRT;
                end
            else
                % no recorded RT, impute the RT (RT_adj) by seeking the last "transition point"
                RT_expectation(k) = NaN;
                for l = size(rating_Trajectory{k,2},1):-1:2
                    if (rating_Trajectory{k,2}(l,1) ~= rating_Trajectory{k,2}(l-1,1))...
                            || (rating_Trajectory{k,2}(l,2) ~= rating_Trajectory{k,2}(l-1,2))
                        break
                    end
                end
                if l == 2 && (rating_Trajectory{k,2}(2,1) == rating_Trajectory{k,2}(1,1))...
                            && (rating_Trajectory{k,2}(2,2) == rating_Trajectory{k,2}(1,2))
                    % No movement at all
                    RT_expectation_adj(k) = NaN;
                    expectation_end_x(k) = NaN;
                    expectation_end_y(k) = NaN;
                else
                    % l-1 is when the last movement happened
                    RT_expectation_adj(k) = (l-1)/60;
                    expectation_end_x(k) = rating_Trajectory{k,2}(end,1);
                    expectation_end_y(k) = rating_Trajectory{k,2}(end,2);
                end
            end
            % find decision onset time
            for l = 2:size(rating_Trajectory{k,2}, 1)
                if (rating_Trajectory{k,2}(l,1) ~= rating_Trajectory{k,2}(l-1,1))...
                        || (rating_Trajectory{k,2}(l,2) ~= rating_Trajectory{k,2}(l-1,2))
                    break
                end
            end
            if rating_Trajectory{k,2}(l,1) == rating_Trajectory{k,2}(1,1) && ...
                        rating_Trajectory{k,2}(l,2) == rating_Trajectory{k,2}(1,2)
                        % mouse didn't move at all
                motion_onset_expectation(k) = NaN;
                motion_dur_expectation(k) = NaN;
            else
                motion_onset_expectation(k) = (l-1)/60;
		        if isnan(expectRT)
                    % no response
                    motion_dur_expectation(k) = RT_expectation_adj(k) - motion_onset_expectation(k);
                else
                    motion_dur_expectation(k) = RT_expectation(k) - motion_onset_expectation(k);
                end
            end
        
            % extract experiment conditions (situation and context)
            if k <= 9
                situation_chunk = DesignTable.Situation(DesignTable.Narrative == narratives{r}(rem(i-1, 2)+1));
                situation{k} = situation_chunk{k};
                context_chunk = DesignTable.Context(DesignTable.Narrative == narratives{r}(rem(i-1, 2)+1)); 
                context{k} = context_chunk{k};
            else
                situation_chunk = DesignTable.Situation(DesignTable.Narrative == narratives{r}(2-rem(i-1, 2)));
                situation{k} = situation_chunk{k-9};
                context_chunk = DesignTable.Context(DesignTable.Narrative == narratives{r}(2-rem(i-1, 2))); 
                context{k} = context_chunk{k-9};
            end
        end
    % Make a table for this run
    run_table = addvars(csvData, feeling_end_x, feeling_end_y, RT_feeling, RT_feeling_adj, ...
        motion_onset_feeling, motion_dur_feeling, expectation_end_x, ...
            expectation_end_y, RT_expectation, RT_expectation_adj, ...
            motion_onset_expectation, motion_dur_expectation, ...
            situation, context);%,  'NewVariableNames', ...
           % {'rating_end_x', 'rating_converted', 'RT_adj', 'motion_onset', 'motion_dur'});
    outputFile = fullfile(dataDir, sub, taskname, ...
            strcat(sub, '_ses-02_', taskname, '_run-0', num2str(r), ...
            '_beh-preproc.csv'));
    writetable(run_table, outputFile)
    end
% if rem(i, 10) == 0; disp(i); end  % for test  
end