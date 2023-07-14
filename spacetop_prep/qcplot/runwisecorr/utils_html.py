# %%----------------------------------------------------------------------
#                             plot image in html
# ----------------------------------------------------------------------
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
    display(HTML(html_content))