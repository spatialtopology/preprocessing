<p align="center">
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<img src="https://user-images.githubusercontent.com/54367954/195647242-1258eaf4-f838-43ea-b65c-f94dfe005e6b.png" width="500">
    </p>
<h1 align="center">
    spacetop preprocessing
    </h1>

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
<h4 align="center">
    Code for preprocessing fMRI, physiogical and behavioral data
    </h4>




Table of contents
-----------------

* [About](#about)
* [Prerequisites](#prerequisites)
* [Usage](#usage)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Contributors](#contributors)
* [Acknowledgments](#acknowledgments)


About
-----------------
`spacetop-prep` is a repository that hosts a number of codes for preprocessing data, collected under the [Spatial Topology grant](https://www.nibib.nih.gov/node/133216). 
- Preprocessing entails data cleaning of **fMRI, physiological, and behavioral data**, using both open-source containers such as fmriprep or custom built code specifically for the Spatial Topology dataset. 
- The goal of this repository is two-folds: **reproducibility** of the preprocessing steps in the spacetop universe, and **generalizatbility** for other users planning to preprocess BIDS-formatted fMRI, physio, and behavioral data. 
- Each folder is intended to serve as an independent module of its own. Please go through each README underneath each modular folder, which will walk you through the prerequisites, usage, and relevant questions. 

Prerequisites
-----------------
For the physiological data preprocesing, please install the following conda environment, [phyio.yaml](https://github.com/spatialtopology/spacetop-prep/blob/master/spacetop_prep/physio/physio.yaml)

Usage
-----------------
1. `git clone` the repository
2. Run the following code to enable a `spacetop_prep` module. 


<div style="background: #FFFFFF; color: #000">

```
python setup.py sdist
pip install -e .
```

</div>

3. Import a module. For example

```
from spacetop_prep.physio import utils
```

    *  [physio](https://github.com/spatialtopology/spacetop-prep/tree/master/spacetop_prep/physio) @jungheejung
    *  [redcap](https://github.com/spatialtopology/spacetop-prep/tree/master/spacetop_prep/redcap) @jungheejung

Getting help
-----------------
If you have issues or any suggestions, please use our Issues tab. We have sections for 
- 🐞 bug report, 
- 💎 feature request
- 📚 documentation request
- 🧠 logging in duplicate scans for datalad users.

Based on your input, we plan to compile a generic Wiki with Q&As for future users. 

Contributing
-----------------
Thank you for your interest in making spacetop-prep a better resource. 

#### Submitting changes 
* Please send a GitHub Pull Request to spacetop-prep with a clear list of what you've done (read more about [pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)). 
* Please follow our coding conventions (below) and make sure all of your commits are atomic (one feature per commit).
* Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:
```
$ git commit -m "${TAG}: A brief summary of the commit
> 
> A paragraph describing what changed and its impact."
```
#### Coding conventions
* We indent using four spaces
* We ALWAYS put spaces after list items and method parameters ([1, 2, 3], not [1,2,3]), around operators (x += 1, not x+=1), and around hash arrows.
* We strive to use relative paths instead of absolute paths. In cases where absolute paths are needed, consider using arguments outside of python script, using argparse or click. 
* For commit messages, we use tags, follow the convention of Numpy: check out documentation ["writing the commit message"] (https://numpy.org/doc/stable/dev/development_workflow.html?highlight=maint#writing-the-commit-message)

License
-----------------
This README is distributed under the terms of MIT License. For further details, check our [LICENSE.md](https://github.com/spatialtopology/spacetop-prep/blob/master/LICENSE.md)

Contributors
------------------

* Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)). 
* This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. 
* Contributions of any kind are welcome!

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
     <tr>
      <td align="center"><a href=""><img src="https://user-images.githubusercontent.com/54367954/206926455-5c94bd35-ab38-4a1f-bc78-d0503c52bd40.png" width="100px;" alt="Heejung Jung"/><br /><sub><b>Heejung Jung</b></sub></a><br /><a href="#infra-jungheejung" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Maintenance">🚧</a> 
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Project Management">📆</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Tests">⚠️</a> <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Code">💻</a></td>
      <td align="center"><a href="https://psadil.github.io/psadil"><img src="https://avatars.githubusercontent.com/u/8172767?v=4=100" width="100px;" alt="Patrick Sadil"/><br /><sub><b>Patrick Sadil</b></sub></a><br /><a href="#infra-psadil" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=psadil" title="Tests">⚠️</a> <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=psadil" title="Code">💻</a></td>
      <td align="center"><a href="http://www.onerussian.com"><img src="https://avatars.githubusercontent.com/u/39889?v=4?s=100" width="100px;" alt="Yaroslav Halchenko"/><br /><sub><b>Yaroslav Halchenko</b></sub></a><br /><a href="https://github.com/spatialtopology/spacetop-prep/commits?author=yarikoptic" title="Tests">⚠️</a> <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=yarikoptic" title="Code">💻</a> <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=yarikoptic" title="Mentoring">🧑‍🏫</a></td>
      <td align="center"><a href="https://user-images.githubusercontent.com/54367954/206926403-aab0c902-07fc-4190-9b8c-995563d1b80c.png"><img src="https://user-images.githubusercontent.com/54367954/206926403-aab0c902-07fc-4190-9b8c-995563d1b80c.png" width="100px;" alt="Isabel Neumann"/><br /><sub><b>Isabel Neumann</b></sub></a><br /><a href="#infra-isabeln23" title="Ideas">🤔</a> <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=isabeln23" title="Documentation">📖</a> 
       <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=isabeln23" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->



Acknowledgments
-----------------
Grant funding National Institute of Biomedical Imaging and Bioengineering (NIBIB) [1R01EB026549-01](https://www.nibib.nih.gov/node/133216)


