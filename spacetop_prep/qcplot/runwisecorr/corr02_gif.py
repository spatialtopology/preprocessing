# %%
from PIL import Image
from os.path import join
import os, glob
import pathlib

def gifify(sub, img_dir, save_dir, file_pattern, save_fname):
    image_files = glob.glob(join(img_dir, f"{file_pattern}"))# f"*sbref*.png"))
    images = []
    for filename in sorted(image_files):
        img = Image.open(filename)
        images.append(img)
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
    images[0].save(join(save_dir,  f'{save_fname}'), save_all=True, append_images=images[1:], duration=200, loop=0)#f'animation-sbref_{sub}.gif'), save_all=True, append_images=images[1:], duration=200, loop=0)

# %% List of PNG image filenames

gifify(sub='sub-0002',
       img_dir=f'/Volumes/derivatives/fmriprep_qc/runwisecorr/{sub}',
       save_dir='/Volumes/derivatives/fmriprep_qc/runwisecorr/meangif',
       file_pattern=f"corr_{sub}_x-*.png",
       save_fname=f"animation-meanimg_{sub}.gif")

gifify(sub='sub-0002',
       img_dir=f"/Volumes/derivatives/fmriprep_qc/runwisecorr/{sub}",
       save_dir='/Volumes/derivatives/fmriprep_qc/runwisecorr/maskgif/',
       file_pattern=f"masked*{sub}*.png",
       save_fname=f"animation-masked_{sub}.gif")


gifify(sub='sub-0002',
       img_dir='/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/',
       save_dir='/Volumes/derivatives/fmriprep_qc/sbref/',
       file_pattern=f"*sbref*.png",
       save_fname=f"animation-sbref_{sub}.gif")


