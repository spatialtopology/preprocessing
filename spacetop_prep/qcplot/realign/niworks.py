fname='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep/sub-0002/ses-01/func/sub-0002_ses-01_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'

nipypecli run niworkflows.interfaces.registration EstimateReferenceImage ${fname}


niworkflows.interfaces.reportlets.registration.ANTSApplyTransformsRPT(
    input_image,
    reference_image,
    transforms
    generate_report=True, **kwargs)