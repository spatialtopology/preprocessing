%-----------------------------------------------------------------------
% Job saved on 03-Jul-2023 20:08:21 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.spm.spatial.coreg.estimate.ref = {'/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-01_task-social_acq-mb8_run-01_sbref.nii,1'};
matlabbatch{1}.spm.spatial.coreg.estimate.source = {'/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-01_task-social_acq-mb8_run-04_sbref.nii,1'};
%%
matlabbatch{1}.spm.spatial.coreg.estimate.other = {
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-01_task-social_acq-mb8_run-02_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-01_task-social_acq-mb8_run-03_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-01_task-social_acq-mb8_run-04_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-01_task-social_acq-mb8_run-05_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-01_task-social_acq-mb8_run-06_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-03_task-social_acq-mb8_run-01_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-03_task-social_acq-mb8_run-02_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-03_task-social_acq-mb8_run-03_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-03_task-social_acq-mb8_run-04_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-03_task-social_acq-mb8_run-05_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-03_task-social_acq-mb8_run-06_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-04_task-social_acq-mb8_run-01_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-04_task-social_acq-mb8_run-02_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-04_task-social_acq-mb8_run-03_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-04_task-social_acq-mb8_run-04_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-04_task-social_acq-mb8_run-05_sbref.nii,1'
                                                   '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/sub-0002_ses-04_task-social_acq-mb8_run-06_sbref.nii,1'
                                                   };
%%
matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.cost_fun = 'nmi';
matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.sep = [4 2];
matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];
matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.fwhm = [7 7];
