
# %%
from utils_html import htmlify
import os, glob
from os.path import join
import base64
from IPython.display import HTML
import pathlib
from os.path import join
import os
import ipywidgets as widgets
from IPython.display import display
# List of GIF file paths

def htmlify(img_files, sub, save_dir, file_pattern):
        # Generate HTML content for each GIF image
    html_content = ""
    for gif_file in img_files:
        with open(gif_file, "rb") as file:
            gif_data = file.read()
        gif_base64 = base64.b64encode(gif_data).decode("ascii")
        html_content += f'<img src="data:image/gif;base64,{gif_base64}" /><br>'

    # Save the HTML content to a file
    output_html_file = join(save_dir, f"{file_pattern}")
    pathlib.Path(join(save_dir)).mkdir(parents=True, exist_ok=True)
    with open(output_html_file, "w") as file:
        file.write(html_content)

    # Display the HTML content
    # display(HTML(html_content))
# %%
img_dir ='/Volumes/derivatives/fmriprep_qc/runwisecorr/stdev'
save_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr/stdev_report'
sub_folders = next(os.walk(img_dir))[1]
sub_list = [i for i in sorted(sub_folders) if i.startswith('sub-')]

for sub in sub_list:
    img_files = sorted(glob.glob(join(img_dir, sub, '*.png')))
    sub_save_dir = join(save_dir, sub)
    htmlify(img_files,sub, save_dir=save_dir, file_pattern=f"stdev_{sub}.html")