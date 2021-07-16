# preprocessing
code for transferring data and preprocessing

```
tree structure of git repository
** preprocessing **
.
|-- datalad
|   `--  datalad.sh
|   
|-- data_transfer
|-- preprocessing
|   |-- fmriprep
|   |   |-- fmriprep_pbs
|   |   |   |-- c01_SUBMIT.sh
|   |   |   |-- c02_wrapper.pbs
|   |   |   `-- c03_fmriprep.sh
|   |   |-- fmriprep_slurm
|   |   |   |-- c01_SUBMIT.sh
|   |   |   `-- c02_fmriprep.sh
|   |   `-- README.md
|   `-- mriqc
|       |-- mriqc_pbs
|       |   `-- mriqc_02code.sh
|       `-- mriqc_slurm
|           |-- c01_submit_mriqc_group.sh
|           |-- c01_submit_mriqc.sh
|           `-- c02_mriqc_singularity.sh
```
