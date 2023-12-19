%-----------------------------------------------------------------------
% Job saved on 03-Jul-2023 18:31:29 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
%%
matlabbatch{1}.spm.spatial.realign.estimate.data = {
                                                    {
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-01_task-social_acq-mb8_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-01_task-social_acq-mb8_run-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-01_task-social_acq-mb8_run-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-01_task-social_acq-mb8_run-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-01_task-social_acq-mb8_run-5_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-01_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    }
                                                    {
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-03_task-social_acq-mb8_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-03_task-social_acq-mb8_run-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-03_task-social_acq-mb8_run-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-03_task-social_acq-mb8_run-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-03_task-social_acq-mb8_run-5_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-03_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    }
                                                    {
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-04_task-social_acq-mb8_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-04_task-social_acq-mb8_run-2_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-04_task-social_acq-mb8_run-3_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-04_task-social_acq-mb8_run-4_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-04_task-social_acq-mb8_run-5_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-04_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_desc-preproc_bold.nii,1'
                                                    }
                                                    }';
%%
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.quality = 0.9;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.sep = 4;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.fwhm = 5;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.rtm = 1;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.interp = 2;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.wrap = [0 0 0];
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.weight = '';

spm_jobman('run',matlabbatch);
