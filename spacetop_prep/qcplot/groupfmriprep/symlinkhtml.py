# %%
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import os
import shutil
 # %%
def resolve_symlinks_in_html(url, save_path):
    # Download the HTML file
    urlretrieve(url, save_path)

    # Parse the HTML file
    with open(save_path, 'r') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')

        # Find all image tags with src attributes
        image_tags = soup.find_all('img', src=True)

        # Resolve and update the src attributes of symlinked images
        for image_tag in image_tags:
            src_path = image_tag['src']
            resolved_path = os.path.realpath(src_path)
            image_tag['src'] = resolved_path

    # Save the modified HTML file
    with open(save_path, 'w') as modified_html_file:
        modified_html_file.write(str(soup))

# Example usage
url = 'http://example.com/index.html'
save_path = '/path/to/save/index.html'

url = 'http://0.0.0.0:8081/results/fmriprep/group/consolidated_sdc_001.html'
save_path=  '/Users/h/Downloads/consolidated_sdc_001.html'

resolve_symlinks_in_html(url, save_path)

# %%
