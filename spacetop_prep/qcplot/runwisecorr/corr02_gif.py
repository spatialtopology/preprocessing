# %%
from PIL import Image
from os.path import join
import os, glob, re
import pathlib

# def gifify(sub, img_dir, save_dir, file_pattern, save_fname):
#     image_files = glob.glob(join(img_dir, f"{file_pattern}"))# f"*sbref*.png"))
#     images = []
#     for filename in sorted(image_files):
#         img = Image.open(filename)
#         images.append(img)
#     pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
#     images[0].save(join(save_dir,  f'{save_fname}'), save_all=True, append_images=images[1:], duration=200, loop=0)#f'animation-sbref_{sub}.gif'), save_all=True, append_images=images[1:], duration=200, loop=0)

def gifify(sub, img_dir, save_dir, file_pattern, save_fname):
    image_files = sorted(glob.glob(os.path.join(img_dir, f"{file_pattern}")))
    images = []
    for filename in image_files:
        with Image.open(filename) as img:
            images.append(img.copy())
            pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
            images[0].save(os.path.join(save_dir, f'{save_fname}'), save_all=True, append_images=images[1:], duration=200, loop=0)

img_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr/'
sub_folders = next(os.walk(img_dir))[1]
sub_list = [i for i in sorted(sub_folders) if i.startswith('sub-')]
# %%
for sub in sub_list:
	gifify(sub=sub,
			img_dir=join(img_dir, sub),
			save_dir=join(img_dir, 'meangif'),
			file_pattern=f"corr_{sub}_x-*.png",
			save_fname=f"animation-meanimg_{sub}.gif")
# %%
for sub in sub_list:
	gifify(sub=sub,
       img_dir=join(img_dir, sub),
       save_dir=join(img_dir, 'maskgif'),
       file_pattern=f"masked*{sub}*.png",
       save_fname=f"animation-masked_{sub}.gif")
# %%
for sub in sub_list:
	gifify(sub='sub-0002',
		img_dir='/Users/h/Documents/projects_local/sandbox/fmriprep_bold/sbref/',
		save_dir='/Volumes/derivatives/fmriprep_qc/sbref/',
		file_pattern=f"*sbref*.png",
		save_fname=f"animation-sbref_{sub}.gif")


# %% try 2
import os
import glob
import re
from PIL import Image

img_dir ='/Volumes/derivatives/fmriprep_qc/runwisecorr/'
sub_folders = next(os.walk(img_dir))[1]
sub_list = [i for i in sorted(sub_folders) if i.startswith('sub-')]
# %%
for sub in sub_list[81:]:
    desired_height = 500
    
    runwise_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr/'
    save_dir = os.path.join(img_dir, 'stdev', sub)
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
        
    # save_fname = f"animation-sdtop2_{sub}.gif"
    
    flist_sd = glob.glob(os.path.join(runwise_dir, sub, "sd-top2_*.png"), recursive=True)
    resized_images = []
    for ind, sdfname in enumerate(flist_sd):
        fpattern = re.search(r"sd-top2_(.*)", sdfname).group(1)
        scatterfname = glob.glob(os.path.join(runwise_dir, sub, f"scatter_{fpattern}"))[0]
        sdbottomfname = glob.glob(os.path.join(runwise_dir, sub, f"sd-bottom2_{fpattern}"))[0]
            
        image1 = Image.open(sdfname)
        image2 = Image.open(scatterfname)
        image3 = Image.open(sdbottomfname)
        
        new_width1 = int(image1.width * desired_height / image1.height)
        new_width2 = int(image2.width * desired_height / image2.height)
        new_width3 = int(image3.width * desired_height / image3.height)
        
        newimage1 = image1.resize((new_width1, desired_height))
        newimage2 = image2.resize((new_width2, desired_height))
        newimage3 = image3.resize((new_width3, desired_height))
        
        combined_image = Image.new("RGB", (new_width1 + new_width2 + new_width3, desired_height))
        combined_image.paste(newimage1, (0, 0))
        combined_image.paste(newimage2, (new_width1, 0))
        combined_image.paste(newimage3, (new_width1 + new_width2, 0))
        combined_image.save(
              os.path.join(save_dir, 'stdev_'+fpattern),
                      )
