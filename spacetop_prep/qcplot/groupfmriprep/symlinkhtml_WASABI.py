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
# url = 'http://example.com/index.html'
# save_path = '/path/to/save/index.html'

# url = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep/group/consolidated_sdc_001.html'
# save_path=  '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/groupfmriprep/consolidated_sdc_001.html'

# MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/scripts/biopac/wasabi-prep/spacetop_prep/qcplot'
# QCDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc'
# FMRIPREPDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/'
# SAVEDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/runwisecorr'
# SCRATCHDIR='/dartfs-hpc/scratch/$USER'
# CANLABDIR='/dartfs-hpc/rc/lab/C/CANlab/modules/CanlabCore'
# PYBIDSDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/1080_wasabi/1080_wasabi_BIDSLayout'

url = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/results/fmriprep/group/consolidated_sdc_001.html'
save_path= '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/groupfmriprep/consolidated_sdc_001.html'

resolve_symlinks_in_html(url, save_path)

# %%
/Volumes/derivatives/fmriprep/results/fmriprep/group/consolidated_sdc_000.html
        output_file = os.path.join(save_dir, f'{sub}_fmriprepSDC_output.html')
        svg_files = glob.glob(os.path.join(directory, sub, 'figures/*sdc_bold.svg'), recursive=True)
        # Create the HTML file
        with open(output_file, 'w') as html_file:
            # Write the HTML header
            html_file.write('<html><body>\n')

            # Iterate over the PNG files
            for svg_file in sorted(svg_files):
                # Get the filename without the directory path
                filename = os.path.basename(svg_file)
                # filename = svg_file
                
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                    svg_html = f'<div>{svg_content}</div>\n'

                # Write the header and image tag for each file
                    html_file.write('<h2>{}</h2>\n'.format(filename))
                # html_file.write('<object data="{}" type="image/svg+xml"></object>\n'.format(svg_file))
                    html_file.write('{}'.format(svg_html))
                
            # Write the HTML footer
            html_file.write('</body></html>\n')

    print('HTML file generated successfully.')