<p align="center">
    <img src="https://user-images.githubusercontent.com/54367954/195647242-1258eaf4-f838-43ea-b65c-f94dfe005e6b.png" width="600">
    </p>
<h1 align="center">
    spacetop preprocessing
    </h1>
<h4 align="center">
    Code for transferring data, tallying, and preprocessing
    </h4>
<p align="center">
   <a href="https://github.com/badges/shields/graphs/contributors" alt="Contributors">
         <img src="https://img.shields.io/badge/Code-React-informational?style=flat&logo=react&color=61DAFB" /></a>
   <a href="https://github.com/spatialtopology/preprocessing" alt="Backers on Open Collective">
         <img src="https://img.shields.io/badge/status-dev-brightgreen"/></a>
   <a href="https://github.com/spatialtopology/preprocessing">
         <img src="https://img.shields.io/badge/contributions-welcome-orange"></a>
   <a href="https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt">
         <img src="https://img.shields.io/badge/license-MIT-blue"></a>
</p>

Code for transferring data, tallying, and preprocessing


Table of contents
-----------------

* [About](#about)
* [Prerequisites](#prerequisites)
* [Usage](#usage)
* [Questions](#questions)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Authors and history](#authors-and-history)
* [Acknowledgments](#acknowledgments)


About
-----------------

Prerequisites
-----------------

Usage
-----------------

Questions
-----------------

Getting help
-----------------

Contributing
-----------------

License
-----------------

Authors and history
-----------------
* Heejung Jung
* Patrick Sadil

Acknowledgments
-----------------
Grant funding National Institute of Biomedical Imaging and Bioengineering (NIBIB) 1R01EB026549-01

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
