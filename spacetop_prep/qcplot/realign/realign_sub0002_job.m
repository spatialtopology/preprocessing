%-----------------------------------------------------------------------
% Job saved on 03-Jul-2023 18:16:42 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
%%

matlabbatch = cell(1,1);
fdir = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref';
%% run once
% flist = filenames(fullfile(fdir, '*'));
% for i = 1:numel(flist)
%     gzFilePath = flist{i};
%     gunzip(gzFilePath);
    
%     % Get the path of the uncompressed file
%     uncompressedFilePath = erase(gzFilePath, '.gz');
%     % Delete the gzipped file if desired
%     delete(gzFilePath);
% end
%

flist = filenames(fullfile(fdir, '*'));

% for i = 1:length(flist)
matlabbatch{1}.spm.spatial.realign.estimate.data = char(flist);
%%

matlabbatch{1}.spm.spatial.realign.estimate.eoptions.quality = 0.9;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.sep = 4;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.fwhm = 0;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.rtm = 1;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.interp = 2;
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.wrap = [0 0 0];
matlabbatch{1}.spm.spatial.realign.estimate.eoptions.weight = '';
spm_jobman('run',matlabbatch);
clearvars matlabbatch