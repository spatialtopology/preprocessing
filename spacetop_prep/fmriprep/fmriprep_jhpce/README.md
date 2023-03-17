# fMRIPrep at JHPCE

Please first review the readme at `mriqc/mriqc_jhpce/README.md`. The general strategy outlined
there applies for fMRIPrep. The only difference is that, rather than processing runs and tasks
separately, jobs are distinguished by sub, modality, and task. That is, the assumption is that a list of
subs are generated (`write_subs`), and then this list is used for running `fmriprep-anat.qsub`. After
a participants anatomical has been successfully processed, all scans for the individual tasks are
analyzed.

Determining which participants have finished successfully is a bit more complicated than with
MRIQC, in that the list of files is different for each participants. The strategy was
to parse the log files (e.g., `find_finished`) and then compare the list of logs indicating successful
completion against the full list of participants (`update_subs.R`).

## Notes

Ideally, the anatomical derivatives would be reused for each of the tasks. At the moment, fMRIPrep
does not have a mechanism for doing this, and so processing each functional task involves regenerating
the anatomicals (although FreeSurfer does not need to be rerun). For this reason, it is recommended
that the task derivatives be output to separate directories and then combined after the fact.

The working directories are very large; each task generates a folder that is ~300-500 Gb. Plan to
delete these folders periodically. The scripts here do not delete them automatically because they
were being stored on a drive running the Lustre filesystem, and it appears that too many parallel
deletions were causing the servers to become desynchronized. For this reason, working directories
were deleted in batches serially. Also that simply calling `rm -r` appears to contribute to
the issues, and so files were instead deleted by running

```bash
find <src> \( -type f -o -type l \) -delete \
  && find <src> -type d -delete
```
