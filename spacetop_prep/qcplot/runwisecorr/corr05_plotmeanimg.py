# %% libraries
import os, glob, re
import shutil
import gzip
from os.path import join
import nilearn
from nilearn import image, plotting, masking
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools
import pathlib
import argparse

from bids import BIDSLayout

# %% -------------------------------------------------------------------
#                               parameters 
# ----------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--slurm-id", 
                    type=int, help="slurm id in numbers")
parser.add_argument("--qcdir", 
                    type=str, help="the top directory of fmriprep preprocessed files")
parser.add_argument("--fmriprepdir", 
                    type=str, help="the top directory of fmriprep preprocessed files")
parser.add_argument("--savedir", 
                    type=str, help="the directory where you want to save your files")
parser.add_argument("--scratchdir", 
                    type=str, help="the directory where you want to save your files")
parser.add_argument("--canlabdir", 
                    type=str, help="the directory where you want to save your files")
args = parser.parse_args()
slurm_id = args.slurm_id
qc_dir = args.qcdir
fmriprep_dir = args.fmriprepdir
save_dir = args.savedir
scratch_dir = args.scratchdir
canlab_dir = args.canlabdir
print(f"{slurm_id} {qc_dir} {fmriprep_dir} {save_dir} {scratch_dir}")

npy_dir = join(qc_dir, 'numpy_bold')
sub_folders = next(os.walk(npy_dir))[1]
sub_list = [i for i in sorted(sub_folders) if i.startswith('sub-')]
sub = sub_list[slurm_id]#f'sub-{sub_list[slurm_id]:04d}'
print(f" ________ {sub} ________")

pathlib.Path(join(scratch_dir, sub)).mkdir( parents=True, exist_ok=True )
npy_flist = sorted(glob.glob(join(npy_dir, sub, '*.npy'), recursive=True))

# %% -------------------------------------------------------------------
#                               main code 
# ----------------------------------------------------------------------

# construct an index list _____________________________________________________
# index_list = []
# sessions = ['ses-01', 'ses-03', 'ses-04']
# runs = ['run-01', 'run-02', 'run-03', 'run-04', 'run-05', 'run-06']

# for i, session in enumerate(sessions):
#     for j, run in enumerate(runs):
#         index = i * len(runs) + j 
#         index_list.append((index, f"{session}_{run}"))

corrdf = pd.DataFrame(index=range(len(index_list)), columns=range(len(index_list)))

index_list = [(i, "ses-" + re.search(r'ses-(\d+)', path).group(1) + "_run-" + re.search(r'run-(\d+)', path).group(1) +"_task-"+re.search(r'task-(.+?)_', path).group(1))  for i, path in enumerate(npy_flist)]

# Load the mask outside the loop, as it's the same for all iterations
mask_fname = join(canlab_dir, 'CanlabCore/canlab_canonical_brains/Canonical_brains_surfaces/brainmask_canlab.nii')
mask_fname_gz = mask_fname + '.gz'
brain_mask = image.load_img(mask_fname_gz)

# Convert index_list to a dictionary for faster lookup
index_dict = {subses: index for index, subses in index_list}

for a, b in itertools.combinations(npy_flist, 2):
    print(a, b)
    # 1. get index _____________________________________________________
    # Extract the integers following 'ses-' and 'run-'
    a_ses = int(re.search(r'ses-(\d+)', a).group(1))
    a_run = int(re.search(r'run-(\d+)', a).group(1))
    b_ses = int(re.search(r'ses-(\d+)', b).group(1))
    b_run = int(re.search(r'run-(\d+)', b).group(1))
    # Reconstruct the 'ses-XX_run-XX' string
    a_subses = f"ses-{a_ses:02d}_run-"+re.search(r'run-(\d+)', a).group(1)+"_task-"+re.search(r'task-(.+?)_', a).group(1)
    b_subses = f"ses-{b_ses:02d}_run-"+re.search(r'run-(\d+)', b).group(1)+"_task-"+re.search(r'task-(.+?)_', b).group(1)

    a_index = index_dict.get(a_subses)
    b_index = index_dict.get(b_subses)

    a_matching_index = None
    b_matching_index = None

    # for index, subses in index_list:
    #     if subses == a_subses:
    #         a_index = index
    #         break
    # for index, subses in index_list:
    #     if subses == b_subses:
    #         b_index = index

# 2. mask run 1 and run 2 _____________________________________________________
    # mask_fname = join(canlab_dir, 'CanlabCore/canlab_canonical_brains/Canonical_brains_surfaces/brainmask_canlab.nii')
    # mask_fname_gz = mask_fname + '.gz'
    # brain_mask = image.load_img(mask_fname_gz)

    # imgfname = glob.glob(join(nifti_dir, sub, f'{sub}_{ses}_*_runtype-vicarious_event-{fmri_event}_*_cuetype-low_stimintensity-low.nii.gz'))
    # ref_img_fname = '/Users/h/Documents/projects_local/sandbox/sub-0061_ses-04_task-social_acq-mb8_run-6_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
    # ref_img_fname = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sub-0002_ses-01_task-social_acq-mb8_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii'
    ref_img_fname = join(fmriprep_dir, sub, f"ses-{a_ses:02d}", 'func', f"{sub}_ses-{a_ses:02d}_{task}*_acq-mb8_run-"+re.search(r'run-(\d+)', a).group(1)+"_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")
    ref_img = image.index_img(image.load_img(ref_img_fname),8) #image.load_img(ref_img_fname)
       
    threshold = 0.5
    nifti_masker = nilearn.maskers.NiftiMasker(mask_img= masking.compute_epi_mask(image.load_img(mask_fname_gz), lower_cutoff=threshold, upper_cutoff=1.0),
                                target_affine = ref_img.affine, target_shape = ref_img.shape, 
                         memory_level=1) #memory="nilearn_cache",
    
# 3. check if they plot correctly back into a brain map (nii) _____________________________________________________
    # convert back to 3d brain
    singlemasked = []
    for img_fname in [a, b]:
        img = np.load(img_fname)
        singlemasked.append(
            nifti_masker.fit_transform(
        image.new_img_like(ref_img,img))
        )
    # convert back to 3d brain DEP
    masked_X = nifti_masker.inverse_transform(singlemasked[0])
    masked_img_X = image.new_img_like(ref_img, masked_X.get_fdata()[..., 0])
    plotting.plot_stat_map(masked_img_X, 
                           cut_coords=(0,0,0),
                           title=f"masked img: {sub} ses-{a_ses:02d} run-{a_run:02d}")
    plt.savefig(join(scratch_dir, sub, f"maskedimage_{sub}_{a_subses}.png"))
    plt.close()
# %%

import base64
from IPython.display import HTML
plot_dir = img_dir
# List of GIF file paths
gif_files = [
    join(plot_dir, sub, f"animation-masked_{sub}.gif"),
    join(qc_dir, "sbref", f"animation-sbref_{sub}.gif")
]

# Generate HTML content for each GIF image
html_content = ""
for gif_file in gif_files:
    with open(gif_file, "rb") as file:
        gif_data = file.read()
    gif_base64 = base64.b64encode(gif_data).decode("ascii")
    html_content += f'<img src="data:image/gif;base64,{gif_base64}" /><br>'

# Save the HTML content to a file
output_html_file = join(plot_dir, sub, "multiple_gifs.html")
with open(output_html_file, "w") as file:
    file.write(html_content)

# Display the HTML content
display(HTML(html_content))