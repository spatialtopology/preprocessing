from ..initialize import _extract_bids

def test_extract_bids_num():
	assert _extract_bids("sub-123.nii.gz", "sub") == "123"

    # for numpy it would be smth like
    #import numpy as np
    #assert np.all(binarize(range(5), 2) == np.array([0, 0, 0, 1, 1]))
