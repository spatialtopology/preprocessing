# Overview
* I check the scannotes and cross check datalad to determine files to be removed. 

* If scannote declares "no_data", check if BOLD exists. if so, a) double check the scannotes and b) check the length of image size in order to determine file delete. 
* If scannote declares "no_data", and no BOLD nor behavioral data exists, data was not collected from the get go
* If scannote declares "complete_dontuse", double check scannotes and determine file delete. 