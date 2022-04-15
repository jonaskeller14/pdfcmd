import pikepdf
from optparse import OptionParser
from glob import glob
import os

parser = OptionParser("Script to modify pdf-files (rotate, extract, delete pages, etc.).")
parser.add_option("-f", "--file",       action="append",    type="string",  dest="filenames",       help="")  # TODO: help
parser.add_option("-r", "--rotate",     action="append",    type="string",  dest="rotations",       help="")  # TODO: help
parser.add_option("-d", "--delete",     action="append",    type="string",  dest="deletions",       help="")  # TODO: help
parser.add_option("-m", "--merge",      action="store_true",                dest="merge",           help="")  # TODO: help
parser.add_option("-e", "--extract",    action="store",                     dest="extract",         help="")  # TODO: help
parser.add_option("-s", "--split",      action="store",                     dest="split",           help="")  # TODO: help
options, args = parser.parse_args()

# TODO: Immernoch durchsuchbar?

def main():
    # 1 Read
    pdfs, filenames = read()

    # 2.1 Rotate
    if options.rotations is not None:
        pdfs = [rotate(pdf) for pdf in pdfs]

    # 3 Save
    for filename, pdf in zip(filenames, pdfs):
        save((pdf, filename))


def read() -> tuple:
    """
    Reads PDF file(s) and returns list.
    :return:
    """
    # Check paths
    filenames = []
    for filename in options.filenames:
        if os.path.exists(filename):
            filenames.append(filename)
        else:
            filenames += glob(filename)
    # Read pdfs
    pdfs = []
    for filename in filenames:
        print(filename)
        pdfs.append(pikepdf.Pdf.open(filename, allow_overwriting_input=True))
    return pdfs, filenames


def save(*pdf_and_paths):
    """
    Saves pdf to disk.
    :param pdf_and_paths: tuple of len 2: (<pdf>, <filepath>)
    :return:
    """
    for pdf_and_path in pdf_and_paths:
        pdf_and_path[0].save(pdf_and_path[1])


def rotate(pdf):
    """
    Syntax:
    Rotate left = Rotate counterclockwiese = L
    #TODO R2n und H2n+1
    :param pdf:
    :return:
    """

    n = len(pdf.pages)

    for rotation in options.rotations:
        # Determine requested pages for rotation
        all_idx = [False for _ in range(n)]
        sequences = rotation[1:].split(",")
        for seq in sequences:
            seq = seq.strip()
            if seq.isdigit() and 0 <= int(seq)-1 < n:
                all_idx[int(seq)-1] = True
            elif "n" in seq:
                pass  # TODO
            elif "-" in seq:
                lower, upper = [int(i) for i in seq.split("-")]
                all_idx[lower-1:upper] = [True for _ in range(lower-1, upper)]
        # Apply Rotation
        mode = rotation[0]
        for idx, entry in enumerate(all_idx):
            if entry:
                if mode == "R":
                    try:
                        pdf.pages[idx].Rotate += 90
                    except AttributeError:
                        pdf.pages[idx].Rotate = 90
                elif mode == "L":
                    try:
                        pdf.pages[idx].Rotate += -90
                    except AttributeError:
                        pdf.pages[idx].Rotate = -90
                elif mode == "V":
                    try:
                        pdf.pages[idx].Rotate += 180
                    except AttributeError:
                        pdf.pages[idx].Rotate = 180
    return pdf


def merge(*pdfs):
    pass


if __name__ == "__main__":
    main()


