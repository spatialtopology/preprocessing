# %% -------------------------------------------------------------------
#                               libraries 
# ----------------------------------------------------------------------
import pandas as pd 
import matplotlib.pyplot as plt
import os, glob, sys, re
from os.path import join
from nilearn import image
import numpy as np
import seaborn as sns
import json
import argparse
from pathlib import Path
import psutil
import matplotlib.patches as patches
import base64
import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import base64
import ipywidgets as widgets
from IPython.display import display

# %% -------------------------------------------------------------------
#                               functions 
# ----------------------------------------------------------------------
def plot_corr_pair(plot_dir, sub, corr_df, index_list, title):
    from PIL import Image, ImageDraw, ImageFont
    from IPython.display import display
    from matplotlib import font_manager
    from PIL import Image, ImageDraw, ImageFont

    # scale image
    scale_factor = 0.6
    font_size = 40
    # Define the font size
    font = font_manager.FontProperties(family='sans-serif', weight='regular')
    file = font_manager.findfont(font)
    print(file)
    font = ImageFont.truetype(file, 30)

    for i, ind in enumerate(index_list):
        # plot_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr'
        img_name = join(plot_dir, sub, f"corr_{sub}_x-{corr_df.columns[ind[0]+1]}_y-{ind[1]}.png")
        corr_value = corr_df.at[ind[0], ind[1]]  # Get the value from the DataFrame

        image = Image.open(img_name)
        new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
        resized_image = image.resize(new_size)
        # add text
        draw = ImageDraw.Draw(resized_image)
        text = f"{title}: {np.round(corr_value, 5)}"
        text_position = (10, 10)  # Adjust the position according to your requirements
        draw.text(text_position, text, fill="black", font=font)#, font=font)

        # display(resized_image)
        title_str = f"{title}".replace(" ", "")
        save_path = join(plot_dir, sub, f"corr-{title_str}_{sub}_index-{i}.png")
        resized_image.save(save_path, "PNG")


def create_html_with_plots(plots, html_fname):
    # Start building the HTML content
    html_content = "<html><body>"

    # Loop through each plot and save it as an image file
    for i, plot in enumerate(plots):
        # Save the plot as a PNG image file
        image_path = f"plot_{i}.png"
        plot.savefig(image_path)
        plt.close(plot)  # Close the plot to free up memory

        # Create the <img> tag with the image path as the source
        img_tag = f"<img src='{image_path}'></img>"
        
        # Add the image tag to the HTML content
        html_content += img_tag

    # Close the HTML content
    html_content += "</body></html>"

    # Write the HTML content to a file
    with open(html_fname, "w") as file:
        file.write(html_content)
# %% -------------------------------------------------------------------
#                               argparse 
# ----------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--slurm-id", 
                    type=int, help="slurm id in numbers")
parser.add_argument("--img-dir", 
                    type=str, help="the directory where all the QC derivatives are saved")
parser.add_argument("--bad-run", 
                    type=str, help="the top directory of fmriprep preprocessed files")
parser.add_argument("--no-intend", 
                    type=str, help="where the runwise corr will be saved")
parser.add_argument("--task", 
                    type=str, help="the directory where you want to save your files")
args = parser.parse_args()
slurm_id = args.slurm_id
img_dir = args.img_dir
bad_run = args.bad_run
nointendfor = args.no_intend
task = args.task

# img_dir = '/Volumes/derivatives/fmriprep_qc/runwisecorr/' # TODO: SLURM
# bad_run = # TODO: SLURM
# task = # TODO: SLURM
# nointendedfor # TODO: SLURM
sub_folders = next(os.walk(img_dir))[1]
sub_list = [i for i in sorted(sub_folders) if i.startswith('sub-')]
plot_dir = img_dir
sub = sub_list[slurm_id] # TODO: SLURM


# %% -------------------------------------------------------------------
#                               maincode 
# ----------------------------------------------------------------------
corr_df = pd.read_csv(join(img_dir, sub, f'{sub}_runwisecorrelation.csv'))


# ======= NOTE load bad metadata
with open("/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/qcplot/boldcorrelation/bad_runs.json", "r") as json_file:
    bad_dict = json.load(json_file)
bad_runs = []
if bad_dict.get(sub, 'empty') != 'empty':
    bad_runs = bad_dict[sub]

fullruns = corr_df.iloc[:,0]
badrun_strings = []
badrun_indices = []
for badrun in bad_runs:
    bad_number = re.search(r'ses-(\d+)_run-(\d+)', badrun)
    if bad_number:
        ses_number, run_number = bad_number.group(1, 2)
        for i, fullrun in enumerate(fullruns):
            full_number = re.search(r'ses-(\d+)_run-(\d+)', fullrun)
            if full_number and int(full_number.group(1)) == int(ses_number) and int(full_number.group(2)) == int(run_number):
                badrun_indices.append(i)
                badrun_strings.append(fullrun)
                break


# ======= NOTE load fieldmapless metadata
task = 'task-social'
print("load missing fieldmap data metadata")
with open("/Users/h/Documents/projects_local/spacetop-prep/spacetop_prep/qcplot/not_in_intendedFor.json", "r") as json_file:
    missfieldmap_dict = json.load(json_file)
nofieldmap_runs = []
if missfieldmap_dict[task].get(sub, 'empty') != 'empty':
    nofieldmap_runs = missfieldmap_dict[task][sub]

fullruns = corr_df.iloc[:,0]
nofieldmap_indices = []
for nofieldmap in nofieldmap_runs:
    nofieldmap_number = re.search(r'ses-(\d+)_run-(\d+)', nofieldmap)
    if nofieldmap_number:
        ses_nofieldmap, run_nofieldmap = nofieldmap_number.group(1, 2)
        for i, fullrun in enumerate(fullruns):
            full_nofieldmap = re.search(r'ses-(\d+)_run-(\d+)', fullrun)
            if full_nofieldmap and int(full_nofieldmap.group(1)) == int(ses_nofieldmap) and int(full_nofieldmap.group(2)) == int(run_nofieldmap):
                nofieldmap_indices.append(i)
                break


# %% ======= NOTE corerlation plot
# get top, bottom correlation first _____________________________________________________________
clean_corrdf = corr_df.iloc[:, 1:]
top_three_indices = clean_corrdf.stack().nlargest(3).index
bottom_three_indices = clean_corrdf.stack().nsmallest(3).index

# insert 1s in identity line ____________________________________________________________________
num_rows, num_cols = clean_corrdf.shape
for i in range(num_rows):
    j = i   # Calculate the column index based on the row index
    clean_corrdf.iloc[i, j] = 1

# plot heatmap __________________________________________________________________________________
fig, (ax_heatmap) = plt.subplots(1, 1, figsize=(12, 8), gridspec_kw={'width_ratios': [10]})
heatmap = sns.heatmap(clean_corrdf.values, cmap='viridis', annot=False, fmt='.2f', square=True, ax=ax_heatmap)
heatmap.collections[0].colorbar.remove()

# tweak colorbar position _______________________________________________________________________
cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])  # Adjust the position and size of the colorbar
heatmap = ax_heatmap.collections[0]
plt.colorbar(heatmap, cax=cbar_ax)

names = np.array(clean_corrdf.columns)
ticks = np.arange(0, 18)
ax_heatmap.set_xticks(ticks)
ax_heatmap.set_yticks(ticks+1.3)
ax_heatmap.set_xticklabels(names, rotation=60)
ax_heatmap.set_yticklabels(names, rotation=30)

# outline upper triangle grid _____________________________________________________________________
num_rows, num_cols = len(clean_corrdf), len(clean_corrdf)

for i in range(num_rows):
    for j in range(i, num_cols):
        rect = plt.Rectangle((j, i), 1, 1, fill=False, edgecolor='gray', linewidth=.3)
        ax_heatmap.add_patch(rect)

# outline a cell for lowest correlation _________________________________________
for index in bottom_three_indices:
    cell_to_outline = (index[0], clean_corrdf.columns.get_loc(index[1]))#corr_df.columns.get_loc(index[1]) - 1)  # Adjust column index by subtracting 1
    cell_x = cell_to_outline[1] + 0.5  # Calculate the coordinates of the cell
    cell_y = cell_to_outline[0] + 0.5
    rect = plt.Rectangle((cell_x - 0.5, cell_y - 0.5), 1, 1, edgecolor='cyan', linewidth=3, fill=False)
    ax_heatmap.add_patch(rect)

# Get the top three highest correlations _________________________________________
for index in top_three_indices:
    cell_to_outline = (index[0], clean_corrdf.columns.get_loc(index[1]))#corr_df.columns.get_loc(index[1]) - 1)  # Adjust column index by subtracting 1
    cell_x = cell_to_outline[1] + 0.5  # Calculate the coordinates of the cell
    cell_y = cell_to_outline[0] + 0.5
    rect = plt.Rectangle((cell_x - 0.5, cell_y - 0.5), 1, 1, edgecolor='#FFFF00', linewidth=3, fill=False)
    ax_heatmap.add_patch(rect)

# bad runs based on fmriprep image parameters _________________________________________
if badrun_indices:
    for i in np.arange(len(badrun_indices)):
        highlight_row = badrun_indices[i]
        highlight_column = badrun_indices[i]
        num_rows, num_cols = corr_df.shape
        ax_heatmap.add_patch(plt.Rectangle((highlight_column, highlight_row), 1, 1, fill=False, edgecolor='red', lw=3))

# runs with no corresponding fieldmap _________________________________________
if nofieldmap_indices:
    for i in np.arange(len(badrun_indices)):
        highlight_row = nofieldmap_indices[i]
        highlight_column = nofieldmap_indices[i]
        num_rows, num_cols = corr_df.shape
        ax_heatmap.add_patch(plt.Rectangle((highlight_column, highlight_row), 1, 1, fill=False, edgecolor='purple', lw=3))

# Legend _________________________________________
legend_patches = [
    patches.Patch(facecolor='red', edgecolor='gray', label='Bad Runs'),
    patches.Patch(facecolor='purple', edgecolor='gray', label='No Fieldmap Runs'),
    patches.Patch(facecolor='cyan', edgecolor='gray', label='Bottom 3 Correlation'),
    patches.Patch(facecolor='#FFFF00', edgecolor='gray', label='Top 3 Correlation')
]
fig.legend(handles=legend_patches, loc='lower right', bbox_to_anchor=(1.2, 0.0))
ax_heatmap.set_title(f"{sub} heatmap of runwise correlation coefficients")
plt.savefig(join(plot_dir, sub, f"heatmap-runwisecorr_{sub}.png"),  bbox_inches='tight')


# %% ----------------------------------------------------------------------
#                   plot top bottom 3 correlation pairs 
# ----------------------------------------------------------------------
plot_corr_pair(plot_dir=plot_dir, 
                sub=sub,
                corr_df=corr_df, 
                index_list=top_three_indices,
                title="top correlation")
 
plot_corr_pair(plot_dir=plot_dir, 
                sub=sub,
                corr_df=corr_df, 
                index_list=bottom_three_indices,
                title="lowest correlation")
 

# %% ----------------------------------------------------------------------
#                             plot masked image
# ----------------------------------------------------------------------
# masked_fname = join(plot_dir, sub, f"animation-masked_{sub}.gif")
# b64 = base64.b64encode(open(masked_fname,'rb').read()).decode('ascii')
# display(HTML(f'<img src="data:image/gif;base64,{b64}" />'))


# ----------------------------------------------------------------------
#                             plot sbref image
# ----------------------------------------------------------------------
# sbref_fname = join(f"/Volumes/derivatives/fmriprep_qc/sbref/animation-sbref_{sub}.gif")
# b64 = base64.b64encode(open(sbref_fname,'rb').read()).decode('ascii')
# display(HTML(f'<img src="data:image/gif;base64,{b64}" />'))

# plot in one html
# save_path = join(plot_dir, sub, f"corr-top_correlation_{sub}.png")

# %%----------------------------------------------------------------------
#                             plot image in html
# ----------------------------------------------------------------------
import base64
from IPython.display import HTML

# List of GIF file paths
gif_files = [
    join(plot_dir, sub, f"heatmap-runwisecorr_{sub}.png"),
    join(plot_dir, sub, f"corr-topcorrelation_{sub}_index-0.png"),
    join(plot_dir, sub, f"corr-topcorrelation_{sub}_index-1.png"),
    join(plot_dir, sub, f"corr-topcorrelation_{sub}_index-2.png"),
    join(plot_dir, sub, f"corr-lowestcorrelation_{sub}_index-0.png"),
    join(plot_dir, sub, f"corr-lowestcorrelation_{sub}_index-1.png"),
    join(plot_dir, sub, f"corr-lowestcorrelation_{sub}_index-2.png"),
    join(plot_dir, 'maskgif', f"animation-masked_{sub}.gif"),
    join(plot_dir, 'meangif', f"animation-meanimg_{sub}.gif" )
]

# Generate HTML content for each GIF image
html_content = ""
for gif_file in gif_files:
    with open(gif_file, "rb") as file:
        gif_data = file.read()
    gif_base64 = base64.b64encode(gif_data).decode("ascii")
    html_content += f'<img src="data:image/gif;base64,{gif_base64}" /><br>'

# Save the HTML content to a file
output_html_file = join(plot_dir, 'corr_report', f"runwise-corr_{sub}.html")
with open(output_html_file, "w") as file:
    file.write(html_content)

# Display the HTML content
display(HTML(html_content))

# %%
