/usr/local/miniconda/lib/python3.6/site-packages/mriqc/interfaces/viz.py:149: UserWarning: loadtxt: Empty input file: "/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth/derivatives/mriqc/work/workflow_enumerator/funcMRIQC/ComputeIQMs/_in_file_..dartfs-hpc..rc..lab..C..CANlab..labdata..data..spacetop..dartmouth..sub-0005..ses-01..func..sub-0005_ses-01_task-social_acq-mb8_run-02_bold.nii.gz/SpikesFinderFFT/sub-0005_ses-01_task-social_acq-mb8_run-02_bold_valid_spikes.tsv"
  spikes_list = np.loadtxt(self.inputs.in_spikes, dtype=int).tolist()
/usr/local/miniconda/lib/python3.6/site-packages/mriqc/interfaces/viz.py:149: UserWarning: loadtxt: Empty input file: "/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop/dartmouth/derivatives/mriqc/work/workflow_enumerator/funcMRIQC/ComputeIQMs/_in_file_..dartfs-hpc..rc..lab..C..CANlab..labdata..data..spacetop..dartmouth..sub-0005..ses-01..func..sub-0005_ses-01_task-social_acq-mb8_run-03_bold.nii.gz/SpikesFinderFFT/sub-0005_ses-01_task-social_acq-mb8_run-03_bold_valid_spikes.tsv"
  spikes_list = np.loadtxt(self.inputs.in_spikes, dtype=int).tolist()
Traceback (most recent call last):
  File "/usr/local/miniconda/bin/mriqc", line 11, in <module>
    load_entry_point('mriqc==0.14.2', 'console_scripts', 'mriqc')()
  File "/usr/local/miniconda/lib/python3.6/site-packages/mriqc/bin/mriqc_run.py", line 250, in main
    mriqc_wf.run(**plugin_settings)
  File "/usr/local/miniconda/lib/python3.6/site-packages/nipype/pipeline/engine/workflows.py", line 595, in run
    runner.run(execgraph, updatehash=updatehash, config=self.config)
  File "/usr/local/miniconda/lib/python3.6/site-packages/nipype/pipeline/plugins/base.py", line 192, in run
    report_nodes_not_run(notrun)
  File "/usr/local/miniconda/lib/python3.6/site-packages/nipype/pipeline/plugins/tools.py", line 82, in report_nodes_not_run
    raise RuntimeError(('Workflow did not execute cleanly. '
RuntimeError: Workflow did not execute cleanly. Check log for details
