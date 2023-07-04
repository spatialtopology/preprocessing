# %%
from PIL import Image
from os.path import join
import os, glob

# List of PNG image filenames
sub = 'sub-0002'
img_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr/'
image_files = sorted(glob.glob(join(img_dir, sub, f"corr_{sub}_x-*.png")))
# image_files = ['image1.png', 'image2.png', 'image3.png', ...]

# Open each image and append to a list
images = []
for filename in image_files:
    img = Image.open(filename)
    images.append(img)

# Save the images as an animated GIF
# save_dir = (img_dir, sub)
images[0].save(join(img_dir, sub, f'animation_{sub}.gif'), save_all=True, append_images=images[1:], duration=200, loop=0)

# %%
sub = 'sub-0002'
img_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr/'
image_files = glob.glob(join(img_dir, sub, f"masked*{sub}*.png"))
# image_files = ['image1.png', 'image2.png', 'image3.png', ...]

# Open each image and append to a list
images = []
for filename in sorted(image_files):
    img = Image.open(filename)
    images.append(img)

# Save the images as an animated GIF
# save_dir = (img_dir, sub)
images[0].save(join(img_dir, sub, f'animation-masked{sub}.gif'), save_all=True, append_images=images[1:], duration=200, loop=0)

