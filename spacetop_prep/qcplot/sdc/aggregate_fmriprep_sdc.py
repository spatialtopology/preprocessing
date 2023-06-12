#%%
import os
import glob

# This script helps generate a report of all distortion correction images from fmriprep output
__author__ = "Michael Sun"
__credits__ = ["Heejung Jung"] # people who reported bug fixes, made suggestions, et

def generate_html_with_images(directory, save_dir):
    # Find all .svg files recursively in the directory
    sub_list = next(os.walk(directory))[1]
    print(sub_list)
    for sub in sub_list:
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

# Unix:
fmriprep_directory = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'  # Specify the directory path here
save_dir = os.path.join( '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc','sdc' )
output_file = os.path.join(save_dir, 'fmriprepDSC_output.html')# Specify the output HTML file path here

generate_html_with_images(fmriprep_directory, save_dir)
