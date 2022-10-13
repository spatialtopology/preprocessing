<p align="center">
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
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

Contributors
------------------
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
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

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="http://www.onerussian.com"><img src="https://avatars.githubusercontent.com/u/39889?v=4?s=100" width="100px;" alt="Yaroslav Halchenko"/><br /><sub><b>Yaroslav Halchenko</b></sub></a><br /><a href="#infra-yarikoptic" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/spatialtopology/preprocessing/commits?author=yarikoptic" title="Tests">⚠️</a> <a href="https://github.com/spatialtopology/preprocessing/commits?author=yarikoptic" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!