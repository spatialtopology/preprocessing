
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
1) What if the data is shorter than expected run
A: depending on the threshold you provide, the code will identify a block of timepoints as a run or not.
2) what if data is longer than expected (e.g. forgot to start and stop run)?
A: No worries, we're using the channel with the MRtriggers "fMRI Trigger - CBLCFMA - Current Feedba"
The data can't be longer than the MRI protocol, if the criteria is based on the MRtriggers ;)