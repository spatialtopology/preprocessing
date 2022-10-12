<p align="center">
    <a href="https://github.com/badges/shields/graphs/contributors" alt="Contributors">
        <img src="https://img.shields.io/badge/Code-React-informational?style=flat&logo=react&color=61DAFB" /></a>
    <a href="https://github.com/spatialtopology/preprocessing" alt="Backers on Open Collective">
        <img src="https://img.shields.io/badge/status-dev-brightgreen" /></a>
  <--  
  <a href="#sponsors" alt="Sponsors on Open Collective">
        <img src="https://img.shields.io/opencollective/sponsors/shields" /></a>
    <a href="https://github.com/badges/shields/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/badges/shields" /></a>
    <a href="https://circleci.com/gh/badges/shields/tree/master">
        <img src="https://img.shields.io/circleci/project/github/badges/shields/master" alt="build status"></a>
    <a href="https://circleci.com/gh/badges/daily-tests">
        <img src="https://img.shields.io/circleci/project/github/badges/daily-tests?label=service%20tests"
            alt="service-test status"></a>
    <a href="https://coveralls.io/github/badges/shields">
        <img src="https://img.shields.io/coveralls/github/badges/shields"
            alt="coverage"></a>
    <a href="https://lgtm.com/projects/g/badges/shields/alerts/">
        <img src="https://img.shields.io/lgtm/alerts/g/badges/shields"
            alt="Total alerts"/></a>
    <a href="https://discord.gg/HjJCwm5">
        <img src="https://img.shields.io/discord/308323056592486420?logo=discord"
            alt="chat on Discord"></a>
    <a href="https://twitter.com/intent/follow?screen_name=shields_io">
        <img src="https://img.shields.io/twitter/follow/shields_io?style=social&logo=twitter"
            alt="follow on Twitter"></a>
            -->
</p>


# About
Spacetop's preprocessing biopac github is developed to **convert** raw physiological data (.acq) into BIDS-abiding files (.csv)
![Frame 6 (1)](https://user-images.githubusercontent.com/18406041/195249514-ddf01d35-3785-4ea1-a101-06507f896fe3.png)
* We acheive this by using the RF pulses as markers for identifying run transitions.
* From that every run is saved separately into a .csv files, now BIDS-compliant.
* Based on these .csv files, you can treat it as a dataframe and run analyses.

# Usage
```
# step 01: convert .acq
python c01_bidsify_discovery.py
```
```
# step 02: identify run transitions and save as csv
python c02_save_separate_run.py 'local' 'task-social' 300
```

## Details
Steps (TODO coding)
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


Question: Questions:
------------------
Q1) What if the data is shorter than expected run?
A: depending on the threshold you provide, the code will identify a block of timepoints as a run or not.
Q2) what if data is longer than expected (e.g. forgot to start and stop run)?
A: No worries, we're using the channel with the MRtriggers "fMRI Trigger - CBLCFMA - Current Feedba"
The data can't be longer than the MRI protocol, if the criteria is based on the MRtriggers ;)

