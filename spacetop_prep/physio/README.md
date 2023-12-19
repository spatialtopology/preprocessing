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
* [Questions](#common-questions)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Contributors](#contributors)
* [Acknowledgments](#acknowledgments)

About
---------
#### Spacetop's preprocessing physio code will *convert* raw physiological data (.acq) into BIDS-abiding files (.csv) It also introduces some backbone code for skin conductance analyses.
![Frame 6 (1)](https://user-images.githubusercontent.com/18406041/195249514-ddf01d35-3785-4ea1-a101-06507f896fe3.png)
* We achieve this by using the RF pulses as markers for identifying run transitions.
* From that every run is saved separately into a .csv files, now BIDS-compliant.
* Based on these .csv files, you can treat it as a dataframe and run analyses.


Prerequisites 
------------------
This is a submodule of spacetop-prep. Make sure you installed spacetop-prep (Also illustrate in our [main README](https://github.com/spatialtopology/spacetop-prep#usage))

```
python setup.py sdist
pip install -e .
```

</div>

### Are there any installations?

```
conda env create -f physio.yaml
```
* Install the conda environment via [**physio.yaml**](https://github.com/spatialtopology/spacetop-prep/blob/0f352b6bd5a10f15f670936324108689c5a6c95c/physio/physio.yaml), included in this repo.
* If you don't want to install an env via the yaml file, make sure to include the essential modules: [neurokit](https://github.com/neuropsychology/NeuroKit) and [bioread](https://github.com/uwmadison-chm/bioread)
### What does my data structure need to be like?
* You need a **`data`** directory as your top folder
* All of your physiological data, right off the stimulus PC, MUST BE STORED in **`../data/physio01_raw`**.
* (The reason for this is because we want similar data structures across the CANlab.)
* From that, this module will create the following folders, such as **physio02_sort** and **physio03_bids**
<img src="https://user-images.githubusercontent.com/54367954/206929176-13e9ea6d-5a64-466b-9b3a-03c107ed112e.png" width="600">



Usage
----------------

#### 1. Rename to BIDS-compliant format: Sort raw .acq into semi-BIDS format
```
python ${PWD}/c01_bidsifysort.py \
--raw-physiodir ${INPUT_DIR} \
--sub-zeropad ${SUB_ZEROPAD} \
--ses-zeropad ${SES_ZEROPAD} \
--logdir ${LOG_DIR}
```

#### 2. Identify run transitions and save as csv
```
python ${PWD}/c02_save_separate_run.py \
--topdir ${TOPDIR} \
--metadata ${METADATA} \
--slurm_id ${SLURM_ID} \
--stride ${STRIDE} \
--sub-zeropad ${SUB_ZEROPAD} \
--task ${TASK} \
--run-cutoff ${CUTOFF} \
--colnamechange ${CHANGECOL} \
--tasknamechange ${CHANGETASK} \
--exclude_sub 1 2 3 4 5 6

>>> python c02_save_separate_run.py --topdir ./data/physio --metadata ./data/demo/metadata.csv --slurm_id 1 --stride 10 sub-zeropad 4 --task 'task-alignvideos' --run-cutoff 300 --colnamechange ./data/demo/colnamechange.json --exclude_sub 1 2 3 4 5 6
```

#### 3. Preprocess signals and save as csv for group level analyses -- Check out our tutorial!
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/spatialtopology/spacetop-prep/blob/master/spacetop_prep/physio/walkthrough_p01_grouplevel.ipynb)
<br>
```
python ${PWD}/p01_grouplevel_01SCL.py \
--input-physiodir ${PHYSIO_DIR} \
--input-behdir ${BEH_DIR} \
--output-logdir ${OUTPUT_LOGDIR} \
--output-savedir ${OUTPUT_SAVEDIR} \
--metadata ${METADATA} \
--dictchannel ${CHANNELJSON} \
--slurm-id ${SLURM_ID} \
--stride ${STRIDE} \
--zeropad ${ZEROPAD} \
--task ${TASK} \
-sr ${SAMPLINGRATE} \
--ttl-index ${TTL_INDEX} \
--scl-epochstart ${SCR_EPOCH_START} \
--scl-epochend ${SCR_EPOCH_END} \
--exclude_sub 1 2 3 4 5 6
```




<!--
Details Steps (TODO coding)
------------------
1) [x] glob acquisitions files
2) [x] extract information from filenames
3) [x] binarize signals based on MR Trigger channel (received RF pulse)
4) [x] convert dataframe to seconds, instead of 2000 sampling rate.
5) [x] identify transitions
6) [x] check if transition is longer than expected TR (threshold 300 s)
6-1) if longer than threshold, include and save as separate run
6-2) if less than expected, flag and keep a note in the flatlist. Pop that index using boolean mask.
7) [x] save using bids naming convention
-->

Common Questions
------------------
#### Q1) What if the data is shorter than expected run?
> A: Everything depends on the `--run-cutoff` threshold that you provide. Depending on the threshold you provide, the code will identify a block of timepoints as a run or discard it.

#### Q2) what if data is longer than expected (e.g. forgot to start and stop run)?
> A: No worries, we're using the channel with the MRtriggers as our criteria.
The data can't be longer than the MRI protocol, if the criteria is based on the MRtriggers. In other words, we're identifying run boundaries based on the scanner pulse, not on the experimenter's operation.

Getting Help
------------------
If you have issues or any suggestions, please use our Issues tab. We have sections for

🐞 bug report,
💎 feature request
📚 documentation request
🧠 logging in duplicate scans for datalad users.
Based on your input, we plan to compile a generic Wiki with Q&As for future users.

Contributing
------------------
* File and issue and notify the maintainers
* Fork this repository, make changes, test it on your local repo.
* Submit a pull request

License
------------------
This README is distributed under the terms of MIT License. For further details, check our LICENSE.md



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
 <!-- HEEJUNG -->
      <td align="center">
      <a href="github.com/jungheejung"><img src="https://user-images.githubusercontent.com/54367954/206926455-5c94bd35-ab38-4a1f-bc78-d0503c52bd40.png" height="100px;" width="100px;" alt="Heejung Jung"/><br /><sub><b>Heejung Jung</b></sub></a><br />
      <a href="#infra-jungheejung" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Maintenance">🚧</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Project Management">📆</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Tests">⚠️</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=jungheejung" title="Code">💻</a></td>
  <!-- ISABEL -->
      <td align="center">
      <a href="https://github.com/isabeln23"><img src="https://user-images.githubusercontent.com/54367954/206926403-aab0c902-07fc-4190-9b8c-995563d1b80c.png" height="100px;" width="100px;" alt="Isabel Neumann"/><br /><sub><b>Isabel Neumann</b></sub></a><br />
      <a href="#infra-isabeln23" title="Ideas">🤔</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=isabeln23" title="Documentation">📖</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=isabeln23" title="Research">🔬</a> 
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=yarikoptic" title="Code">💻</a>
  <!-- YARIK -->
      <td align="center"><a href="http://www.onerussian.com"><img src="https://avatars.githubusercontent.com/u/39889?v=4?s=100" height="100px;" width="100px;" alt="Yaroslav Halchenko"/><br /><sub><b>Yaroslav Halchenko</b></sub></a><br />
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=yarikoptic" title="Tests">⚠️</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=yarikoptic" title="Code">💻</a>
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=yarikoptic" title="Mentoring">🧑‍🏫</a></td>
  <!-- BETHANY -->
      <td align="center"><a href="https://github.com)/huntb9"><img src="https://user-images.githubusercontent.com/54367954/206929426-d35a4798-3a75-47d2-b8b4-648654426cbe.png" height="100px;" width="100px;" alt="Bethany Hunt"/><br /><sub><b>Bethany Hunt</b></sub></a><br />
      <a href="https://github.com/spatialtopology/spacetop-prep/commits?author=huntb9" title="Ideas">🤔</a> </td>
    </tr>
  </tbody>
</table>
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
* Heejung Jung [@jungheejung](github.com/jungheejung)
* Isabel Neumann (Expertise in Physio data processing, Integrating Neurokit, Identifying appropriate functions) [@isabeln23](https://github.com/isabeln23)
* Yaroslav Halchenko (Mastermind behind modularizing spacetop_prep.physio) [@yarikoptic](https://github.com/yarikoptic)
* Bethany Hunt (Initial suggestions on BIDS convention) [@huntb9]([github.com](https://github.com/huntb9)

Acknowledgments
------------------
Grant funding National Institute of Biomedical Imaging and Bioengineering (NIBIB) [1R01EB026549-01](https://www.nibib.nih.gov/node/133216)
