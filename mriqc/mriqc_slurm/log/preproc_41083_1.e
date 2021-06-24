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
