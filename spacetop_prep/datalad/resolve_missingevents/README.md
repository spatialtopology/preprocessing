In cases where we have an exisiting BOLD, but missing events.tsv file, 
there are a couple of case scenarios
1. The behavioral data was not completely collected, but the TEMP files exist. 
(TEMP files are back-up data where the data was printed out on a trial-by-trial basis, 
therefore does not suffer from a "save" after completion.) The only caveat is that
we need to copy these TEMP files into the d_beh and convert them into BIDS
2. The behavioral data was completely collected, but for some reason, not BIDS transformed.
We can simply rerun the events_to_BIDS conversion and figure out errors from there. 
3. Typo in subject ID, which leads to a missing events.tsv. Once the Typo is resolved, 
we reconvert into BIDS. 
4. No behavioral data whatsoever. Make executive decision of whether it is possible to analyze
the BOLD data, regardless of events files. 
- If timing data is necessary (if trials include jitter), discard
- If timing data is fixed (align videos, narratives), include

