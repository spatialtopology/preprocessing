from PyPDF2 import PdfWriter
from PIL import Image
import os, glob
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image

# def compile_images_to_pdf(image_paths, output_path):
#     pdf_writer = PdfWriter()

#     for image_path in image_paths:
#         # Open the image using Pillow
#         image = Image.open(image_path)
        
#         # Create a new PDF page with the same dimensions as the image
#         #pdf_page = pdf_writer.add_blank_page(width=image.width, height=image.height)
        
#         # Convert the image to PDF format
#         #if image.mode != "RGB":
#         image = image.convert("RGB")

#         # Add the PDF page to the writer
#         pdf_writer.add_page(pdf_page)
#         # pdf_page.merge_page(image)

#     # Save the PDF to the output file
#     with open(output_path, "wb") as output_file:
#         pdf_writer.write(output_file)

def generate_pdf_report(image_paths, output_path):
    # Create a PDF document with a specified paper size (e.g., letter size)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    # Adjust the page width to fit the images
    page_width = 500  # Modify this value to adjust the width of the page

    # Iterate through each image path and add it to the PDF
    for image_path in image_paths:
        # Load the image using ReportLab's Image class
        image = Image(image_path)

        # Get the original image width and height
        original_width, original_height = image.drawWidth, image.drawHeight

        # Calculate the aspect ratio of the image
        aspect_ratio = original_width / original_height

        # Calculate the new dimensions to fit the page width
        new_width = page_width
        new_height = new_width / aspect_ratio

        # If the new height is greater than the page height, scale the image down
        page_height = 700  # Modify the page height as per your requirement
        if new_height > page_height:
            new_height = page_height
            new_width = new_height * aspect_ratio

        # Set the new dimensions for the image
        image.drawWidth = new_width
        image.drawHeight = new_height
        # Add the image to the list of elements to be included in the PDF
        elements.append(image)

    # Build the PDF document with the list of elements
    doc.build(elements)

# Example usage
# qcdir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/fmriprep_bold_correlation'

qcdir = '/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep_qc/fmriprep_bold_correlation'
flist = glob.glob(os.path.join(qcdir, 'sub-*_boldcorrelation.png'))
image_paths = sorted(flist)
output_path = "output.pdf"
# compile_images_to_pdf(image_paths, output_path)
generate_pdf_report(image_paths, output_path)