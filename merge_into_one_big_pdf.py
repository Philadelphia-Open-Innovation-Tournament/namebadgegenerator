import os
import sys
from PyPDF2 import PdfMerger

def combine_pdfs(input_folder=None, output_file='combined.pdf'):
    if input_folder is None:
        input_folder = os.getcwd()

    merger = PdfMerger()

    # Get all PDF files in the folder, excluding 'combined.pdf'
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf') and f != output_file]

    # Sort the files to ensure consistent ordering
    pdf_files.sort()

    # Merge PDFs
    for pdf in pdf_files:
        merger.append(os.path.join(input_folder, pdf))

    # Write the combined PDF to the output file
    output_path = os.path.join(input_folder, output_file)
    merger.write(output_path)
    merger.close()

    return output_path

# Usage:
# python combine_pdfs.py
# python combine_pdfs.py /path/to/pdf/folder
# python combine_pdfs.py /path/to/pdf/folder output.pdf
if __name__ == "__main__":
    input_folder = sys.argv[1] if len(sys.argv) > 1 else None
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'combined.pdf'

    output_file = combine_pdfs(input_folder, output_file)
    print(f"Combined PDF saved as {output_file}")

