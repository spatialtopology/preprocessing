<p align="center">
   <img src="https://user-images.githubusercontent.com/18406041/195505977-bfbf8e61-32d2-4ac7-b23d-192abde3dd1f.png" width="400">
   <br>
   
   <a href="https://github.com/badges/shields/graphs/contributors" alt="Contributors">
         <img src="https://img.shields.io/badge/Code-React-informational?style=flat&logo=react&color=61DAFB" /></a>
   <a href="https://github.com/spatialtopology/preprocessing" alt="Backers on Open Collective">
         <img src="https://img.shields.io/badge/status-dev-brightgreen"/></a>
   <a href="https://github.com/spatialtopology/preprocessing">
         <img src="https://img.shields.io/badge/contributions-welcome-orange"></a>
   <a href="https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt">
         <img src="https://img.shields.io/badge/license-MIT-blue"></a>

</p>

Table of contents
-----------------

* [About](#about)
* [Prerequisites](#prerequisites)
* [Usage](#usage)
* [Questions](#questions)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Contributors](#Contributors)
* [Acknowledgments](#acknowledgments)

About
---------
#### Spacetop's preprocessing physio code will *convert* raw physiological data (.acq) into BIDS-abiding files (.csv) It also introduces some backbone code for skin conductance analyses.
![Frame 6 (1)](https://user-images.githubusercontent.com/18406041/195249514-ddf01d35-3785-4ea1-a101-06507f896fe3.png)
* We acheive this by using the RF pulses as markers for identifying run transitions.
* From that every run is saved separately into a .csv files, now BIDS-compliant.
* Based on these .csv files, you can treat it as a dataframe and run analyses.


Prerequisites 
------------------

### Are there any installations?

```
conda env create -f biopac.yaml
```
* Install the conda environment via [**biopac.yaml**](https://github.com/spatialtopology/preprocessing/blob/0f352b6bd5a10f15f670936324108689c5a6c95c/biopac/biopac.yaml), included in this repo.
* If you don't want to install an env via the yaml file, make sure to include the essential modules: [neurokit](https://github.com/neuropsychology/NeuroKit) and [bioread](https://github.com/uwmadison-chm/bioread)
### What does my data structure need to be like?
[ TODO: insert image of data structure ] 
e.g. physio > physio01_raw / physio02_sort / physio03_bids / physio04_ttl

Usage
----------------
1. Rename to BIDS-compliant format: Sort raw .acq into semi-BIDS format
```
python c01_bidsify_discovery.py
```
2. Identify run transitions and save as csv: NOTE: need to pass in arguments
```
python c02_save_separate_run.py 'local' 'task-social' 300
```
3. Preprocess signals and save as csv for group level analyses<br>
Check out our tutorial!
[![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Naereen/badges)



Details Steps (TODO coding)
------------------
1) [x] glob acquisitions files
2) [x] extract information from filesnames
3) [x] binarize signals based on MR Trigger channel (received RF pulse)
4) [x] convert dataframe to seconds, instead of 2000 sampling rate.
5) [x] identify transitions
6) [x] check if transition is longer than expected TR (threshold 300 s)
6-1) if longer than threshold, include and save as separate run
6-2) if less than expected, flag and keep a note in the flatlist. Pop that index using boolean mask.
7) [x] save using bids naming convention


Questions
------------------
### Q1) What if the data is shorter than expected run?
> A: Depending on the threshold you provide, the code will identify a block of timepoints as a run or not.

### Q2) what if data is longer than expected (e.g. forgot to start and stop run)?
> A: No worries, we're using the channel with the MRtriggers as our criteria.
The data can't be longer than the MRI protocol, if the criteria is based on the MRtriggers ;) In other words, we're identifying run boundaries based on the scanner pulse, not on the experimenter's operation.

Getting Help
------------------
* File and issue and notify the maintainers
* Fork this repository, make changes, test it on your local repo.
* Submit a pull request

Contributing
------------------

License
------------------

Contributors
------------------
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
* Heejung Jung [@jungheejung](github.com/jungheejung)
* Isabel Neumann (Integrating Neurokit, Identifying appropriate functions) [@isabeln23](https://github.com/isabeln23)
* Bethany Hunt (Suggestions on Physio data structure, BIDS convention) [@huntb9]([github.com](https://github.com)/huntb9)

Acknowledgments
------------------

