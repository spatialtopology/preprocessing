# %% libraries
import os, glob, re
import shutil
import gzip
from os.path import join
import nilearn
from nilearn import image, plotting, masking, datasets
# from nilearn.input_data import NiftiLabelsMasker
import nibabel as nib
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
                    type=str, help="the directory where all the QC derivatives are saved")
parser.add_argument("--fmriprepdir", 
                    type=str, help="the top directory of fmriprep preprocessed files")
parser.add_argument("--savedir", 
                    type=str, help="where the runwise corr will be saved")
parser.add_argument("--scratchdir", 
                    type=str, help="the directory where you want to save your files")
parser.add_argument("--canlabdir", 
                    type=str, help="the canlab directory")
parser.add_argument("--task", 
                    type=str, help="the BIDS-designated task key-value pair")
parser.add_argument("--pybids_db", 
                    type=str, help="the pybids database to quickly load up your directory")

args = parser.parse_args()
slurm_id = args.slurm_id
qc_dir = args.qcdir
fmriprep_dir = args.fmriprepdir
save_dir = args.savedir
scratch_dir = args.scratchdir
canlab_dir = args.canlabdir
task = args.task
pybids_db = args.pybids_db

# %%
# Test Parameters:
# slurm_id=4
# qc_dir='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc'
# fmriprep_dir='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/'
# save_dir='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/runwisecorr'
# scratch_dir='/scratch/f003z4j'
# canlab_dir = '/dartfs-hpc/rc/lab/C/CANlab/modules/CanlabCore'
# task = 'task-'
# pybids_db = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/1080_wasabi/1080_wasabi_BIDSLayout'

# %%
# def search_for_pybids_database(start_dir):
#     for root, _, files in os.walk(start_dir):
#         if 'layout_index.sqlite' in files:
#             return root  # Return the directory containing the pybids database
#     return None  # Return None if no valid pybids database is found

# %%
# Search for pybids databases and store the result in a variable
# pybids_db = search_for_pybids_database(pybids_db)

try:
    print("A pybids database was found in directory:", pybids_db, "\n Database loaded.")
    layout = BIDSLayout(fmriprep_dir, database_path=pybids_db)
except NameError:
    print("No pybids database was found. \nGenerating a new database...this may take some time...")
    layout = BIDSLayout(fmriprep_dir, database_path=os.path.join(fmriprep_dir, 'pybids_database'))
    
# %%
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
# # sessions = ['ses-01', 'ses-03', 'ses-04']
# # runs = ['run-01', 'run-02', 'run-03', 'run-04', 'run-05', 'run-06']

# sessions = ['ses-' + str(session) for session in layout.get_sessions(subject=sub.replace('sub-', ''))]
# runs=layout.get_runs(subject=sub.replace('sub-', ''))

# # Create a list of tuples containing session and run
# session_run_pairs = [(ses, run) 
#                      for ses in layout.get_sessions(subject=sub.replace('sub-', ''))
#                      for run in layout.get_runs(subject=sub.replace('sub-', ''), session=ses)]

# wildcard_list = [('*ses-' + str(pair[0]) + '_*_run-' + str(pair[1]) + '*') for i, pair in enumerate(session_run_pairs)]

# import fnmatch

# filtered_flist = [filename for filename in npy_flist 
#                   if any(fnmatch.fnmatch(filename, wildcard) 
#                          for wildcard in wildcard_list)]

# corrdf = pd.DataFrame(index=range(len(filtered_flist)), columns=range(len(filtered_flist)))

# npy_flist=filtered_flist


corrdf = pd.DataFrame(index=range(len(npy_flist)), columns=range(len(npy_flist)))
index_list = [(i, "ses-" + re.search(r'ses-(\d+)', path).group(1) + "_run-" + re.search(r'run-(\d+)', path).group(1) +"_task-"+re.search(r'task-(.+?)_', path).group(1))  for i, path in enumerate(npy_flist)]

# Load the mask outside the loop, as it's the same for all iterations
mask_fname = join(canlab_dir, 'CanlabCore/canlab_canonical_brains/Canonical_brains_surfaces/brainmask_canlab.nii')
mask_fname_gz = mask_fname + '.gz'
brain_mask = image.load_img(mask_fname_gz)

# Convert index_list to a dictionary for faster lookup
index_dict = {subses: index for index, subses in index_list}

high_leverage_regions={}

# %%
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
    #         break
    
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
                        memory_level=1) # memory="nilearn_cache",
    
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
                           title=f"masked img: {sub} ses-{a_ses:02d} run-"+re.search(r'run-(\d+)', a).group(1))
    plt.savefig(join(scratch_dir, sub, f"maskedimage_{sub}_{a_subses}.png"))
    plt.close()

    # 4. calculated correlation between run 1 and run 2 _____________________________________________________
    singlemasked_X = np.mean(singlemasked[0], axis=0)
    singlemasked_Y = np.mean(singlemasked[1], axis=0)
    corr = np.corrcoef(singlemasked_X,singlemasked_Y)[0, 1]
    print("file a: "+a)
    print("file b: "+b)
    print(a_index)
    print(b_index)
    
    corrdf.at[a_index, b_index] = corr#np.mean(correlation_coefficients)#correlation

    # 4-2. 2SD pairs
    # ======= NOTE: calculate highest 2sd voxels
    thres_2sd_X = np.mean(singlemasked_X) + 2 * np.std(singlemasked_X)
    thres_2sd_Y = np.mean(singlemasked_Y) + 2 * np.std(singlemasked_Y)
    sdmask = np.logical_and(singlemasked_X > thres_2sd_X, singlemasked_Y > thres_2sd_Y)

    # Create a mask for pairs greater than the threshold    
    sdmask_arrX = singlemasked_X * sdmask
    sdmask_arrY = singlemasked_Y * sdmask
    sdmask_X = nifti_masker.inverse_transform(sdmask_arrX)
    sdmask_Y = nifti_masker.inverse_transform(sdmask_arrY)
    
    topsdfig, axes = plt.subplots(1, 1, figsize=(10, 5))
    display = plotting.plot_stat_map(sdmask_X, cmap='Blues',
                            title=f"Voxels greater than 2 sd: {sub} {a_subses} and {b_subses}", threshold=thres_2sd_X,
                            display_mode='mosaic', 
                            figure = topsdfig, axes=axes, cut_coords=5, draw_cross=False)
    plt.tight_layout()
    display.savefig(join(scratch_dir, sub, f"sd-top2_{sub}_x-{a_subses}_y-{b_subses}.png"))
    plt.close(topsdfig)
    # ======= NOTE: lowest 2sd voxels
    thres_neg2sd_X = np.mean(singlemasked_X) - 2 * np.std(singlemasked_X)
    thres_neg2sd_Y = np.mean(singlemasked_Y) - 2 * np.std(singlemasked_Y)
    sdmask_neg = np.logical_and(singlemasked_X < thres_neg2sd_X, singlemasked_Y < thres_neg2sd_Y)

    # Create a mask for pairs greater than the threshold
    sdmaskneg_arrX = singlemasked_X * sdmask_neg
    sdmaskneg_arrY = singlemasked_Y * sdmask_neg
    sdmaskneg_X = nifti_masker.inverse_transform(sdmaskneg_arrX)
    sdmaskneg_Y = nifti_masker.inverse_transform(sdmaskneg_arrY)

    bottomsdfig, axes = plt.subplots(1, 1, figsize=(10, 5))
    display = plotting.plot_stat_map(sdmaskneg_X, cmap='Blues',
                            title=f"Voxels less than 2 sd: {sub} {a_subses} and {b_subses}", threshold=2,
                            display_mode='mosaic', figure = bottomsdfig, axes=axes, cut_coords=5, draw_cross=False)
    plt.tight_layout()
    display.savefig(join(scratch_dir, sub, f"sd-bottom2_{sub}_x-{a_subses}_y-{b_subses}.png"))
    plt.close()

    # ======= NOTE: highest leverage voxels
    # Fit a linear regression model
    coefficients = np.polyfit(singlemasked_X, singlemasked_Y, 1)
    model = np.poly1d(coefficients)
    # Calculate the predicted Y values
    predicted_Y = model(singlemasked_X)
    # Calculate the residuals (actual Y - predicted Y)
    residuals = singlemasked_Y - predicted_Y
    # Calculate the leverage of each point
    n = len(singlemasked_X)
    X_mean = np.mean(singlemasked_X)
    X_var = np.var(singlemasked_X)
    leverage = ((singlemasked_X - X_mean) ** 2) / X_var
    # Get the indices of points with highest leverage (you can adjust the threshold as needed)
    threshold_leverage = np.percentile(leverage, 95)  # You can change 95 to the desired threshold
    # high_leverage_indices = np.where(leverage > threshold_leverage)
    
    # Calculate the threshold for outliers based on residuals
    # You can adjust the threshold_resid value to control the sensitivity to outliers
    threshold_resid = np.percentile(np.abs(residuals), 95)  # You can change 95 to the desired threshold

    # Create a mask for highest leverage outliers
    high_leverage_outliers_mask = (leverage > threshold_leverage) & (np.abs(residuals) > threshold_resid)

    # hlmask = np.logical_and(singlemasked_X[high_leverage_mask], singlemasked_Y[high_leverage_mask])
    mask_highleverage = nifti_masker.inverse_transform(high_leverage_outliers_mask)
    
    # ======= NOTE: Output Atlas-Labelled Regions for High-Leverage Voxels
    # Load the harvard-oxford atlas
    atlas_dataset = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
    atlas_filename = atlas_dataset.maps

    # Create a masker object to extract the regions from the atlas
    # masker = NiftiLabelsMasker(labels_img=atlas_filename, standardize=False, detrend=False)
    masker = nilearn.maskers.NiftiMasker(labels_img=atlas_filename, standardize=False, detrend=False)

    # Load the atlas region maps image
    atlas_maps_img = atlas_dataset.maps

    # Resample the atlas region maps to match the shape and affine of the mask
    atlas_maps_img_resampled = image.resample_to_img(atlas_maps_img, mask_highleverage)

    # Use the mask to extract the labels corresponding to the regions in the mask
    masked_atlas_data = image.math_img("img1 * img2", img1=atlas_maps_img_resampled, img2=mask_highleverage)
    labels_data = masked_atlas_data.get_fdata()

    # Extract unique label values from the mask
    unique_labels = np.unique(labels_data[mask_highleverage.get_fdata().astype(bool)])

    # Get the corresponding label names for the unique labels
    mask_labels = [atlas_dataset.labels[int(region_label)] for region_label in unique_labels if 0 <= int(region_label) < len(atlas_dataset.labels)]

    # Exclude label values without corresponding label names from unique_labels
    unique_labels = [region_label for region_label in unique_labels
                    if 0 <= int(region_label) < len(atlas_dataset.labels)
                    and atlas_dataset.labels[int(region_label)] is not None]

    # Print the labels corresponding to the mask
    print("High-Leverage Region Labels corresponding to the Harvard-Oxford Atlas mask:")
    print(mask_labels)
    
    high_leverage_regions[f"{sub}_x-{a_subses}_y-{b_subses}"]=mask_labels
        
    hlfig, axes = plt.subplots(1, 1, figsize=(10, 5))
    display = plotting.plot_stat_map(mask_highleverage, cmap='Reds',
                            title=f"5% highest leverage voxels: {sub} {a_subses} and {b_subses}",
                            display_mode='mosaic', figure = hlfig, axes=axes, cut_coords=5, draw_cross=False)
    # Display both plots
    hlfig.text(1.25, .15, '\n'.join(mask_labels), color='black', fontsize=8, ha='right', va='center', transform=hlfig.transFigure)
    plt.tight_layout()
    
    display.savefig(join(scratch_dir, sub, f"highlev_{sub}_x-{a_subses}_y-{b_subses}.png"))
    plt.close()
        
    # ======= NOTE: Plot:
    # plt.scatter(singlemasked_X, singlemasked_Y)
    plt.scatter(singlemasked_X, singlemasked_Y, c='gray', label='All Data', alpha=0.5 )
    plt.scatter(singlemasked_X[sdmask], singlemasked_Y[sdmask], c='darkgreen', label='2sd < voxel', alpha=0.5)
    plt.scatter(singlemasked_X[sdmask_neg], singlemasked_Y[sdmask_neg], c='darkred', label='voxel < -2sd', alpha=0.5)
    plt.scatter(singlemasked_X[high_leverage_outliers_mask], singlemasked_Y[high_leverage_outliers_mask], c='red', label='5% Highest Leverage', alpha=0.8)
    plt.plot([min(singlemasked_X), max(singlemasked_X)], [min(singlemasked_Y), max(singlemasked_Y)], color='black', linestyle='--')
    plt.xlabel(f"{a_subses}")
    plt.ylabel(f"{b_subses}")
    plt.title(f"Scatter plot for voxels in {sub}_x-{a_subses}_y-{b_subses} ")
    plt.legend()
    plt.savefig(join(scratch_dir, sub, f"scatter_{sub}_x-{a_subses}_y-{b_subses}.png"))
    plt.close()

    # 5. plot runs by overlaying each other _____________________________________________________
    masked_X = nifti_masker.inverse_transform(singlemasked[0])
    masked_Y = nifti_masker.inverse_transform(singlemasked[1])

    coords = (-5, -6, -15)
    fig, axes = plt.subplots(3, 1, figsize=(10, 10))
    display = plotting.plot_anat(image.mean_img(masked_X), cmap='Blues', alpha=0.9, 
                                colorbar=False, black_bg=False, dim=False, title=f"Overlay: {sub} {a_subses} and {b_subses}", 
                                figure = fig, cut_coords=coords, axes=axes[0], draw_cross=False)
    display.add_overlay(image.mean_img(masked_Y), cmap="Reds", alpha = .5)

    plotting.plot_anat(image.mean_img(masked_X), cmap='Reds', alpha=1, colorbar=False, cut_coords=coords, 
                    display_mode='ortho',title=f"{a_subses}", figure = fig,axes=axes[1], black_bg=False, dim=False, draw_cross=False)
    plotting.plot_anat(image.mean_img(masked_Y), cmap='Blues', alpha=1, colorbar=False, cut_coords=coords, 
                    display_mode='ortho', title=f"{b_subses}", figure = fig,axes=axes[2], black_bg=False, dim=False, draw_cross=False)

    display.savefig(join(scratch_dir, sub, f"corr_{sub}_x-{a_subses}_y-{b_subses}.png"))
    plt.close(fig)

# %% save df
corrdf.index = [x[1] for x in index_list]
corrdf.columns = [x[1] for x in index_list]
corrdf.to_csv(join(scratch_dir, sub, f"{sub}_runwisecorrelation.csv"))
if os.path.exists(join(save_dir, sub)):
    shutil.rmtree(join(save_dir, sub))
shutil.copytree(join(scratch_dir, sub), join(save_dir, sub)) #join(save_dir, sub))#, dirs_exist_ok=True)

# Now, save high_leverage_regions to a separate CSV file
# First, convert the dictionary to a DataFrame
high_leverage_regions_df = pd.DataFrame.from_dict(high_leverage_regions, orient='index')

# Save high_leverage_dict DataFrame to a CSV file
high_leverage_regions_df_output_path = join(scratch_dir, sub, f"{sub}_high_leverage_HOatlas_mask.csv")
high_leverage_regions_df.to_csv(high_leverage_regions_df_output_path)
