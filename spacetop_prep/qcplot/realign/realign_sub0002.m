% List of open inputs
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
% Realign: Estimate: Session - cfg_files
nrun = X; % enter the number of runs here
jobfile = {'/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/qcplot/realign/realign_sub0002_job.m'};
jobs = repmat(jobfile, 1, nrun);

'/Users/h/Documents/projects_local/sandbox/fmriprep_bold'
inputs = cell(11, nrun);

for crun = 1:nrun
    inputs{1, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{2, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{3, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{4, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{5, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{6, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{7, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{8, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{9, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{10, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
    inputs{11, crun} = MATLAB_CODE_TO_FILL_INPUT; % Realign: Estimate: Session - cfg_files
end
spm('defaults', 'FMRI');
spm_jobman('run', jobs, inputs{:});
