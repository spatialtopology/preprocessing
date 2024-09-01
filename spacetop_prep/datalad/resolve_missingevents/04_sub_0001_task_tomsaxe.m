% download https://github.com/spatialtopology/task-fractional/blob/DBIC/task-tomsaxe/answer_key.csv
url = 'https://github.com/spatialtopology/task-fractional/blob/DBIC/task-tomsaxe/answer_key.csv?raw=true';
answer_filename = 'answer_key.csv';
outfilename = websave(answer_filename, url);

events_fname = '/Users/h/Documents/projects_local/1076_spacetop/sourcedata/d_beh/sub-0001/task-fractional/sub-0001_ses-04_task-fractional_run-01-tomsaxe_beh.csv';
Tload = readtable(events_fname);
answer = readtable(answer_filename, 'Format','%s%u');

Ttotal = join(Tload, answer, 'LeftKeys', 'event02_filename', 'RightKeys', 'event02_filename');
Ttotal.accuracy = Ttotal.answer == Ttotal.event04_response_key;
accuracy_freq = sum(Ttotal.accuracy);
%% __________________________ save parameter ___________________________________
% events_fname = fullfile(sub_save_dir,[bids_string, '_beh.csv' ]);
writetable(Ttotal,events_fname);
