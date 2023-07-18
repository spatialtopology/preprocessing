from PyPDF2 import PdfWriter
from PIL import Image
import os, glob
def compile_images_to_pdf(image_paths, output_path):
    pdf_writer = PdfWriter()

    for image_path in image_paths:
        # Open the image using Pillow
        image = Image.open(image_path)

        # Convert the image to PDF format
        pdf_page = image.convert("RGB")

        # Add the PDF page to the writer
        pdf_writer.add_page(pdf_page)

    # Save the PDF to the output file
    with open(output_path, "wb") as output_file:
        pdf_writer.write(output_file)

# Example usage
qcdir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/fmriprep_bold_correlation'
flist = glob.glob(os.path.join(qcdir, 'sub-*task-social_boldcorrelation.png'))
image_paths = sorted(flist)
output_path = "output.pdf"
compile_images_to_pdf(image_paths, output_path)