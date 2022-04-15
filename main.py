from borb.pdf.pdf import PDF
from optparse import OptionParser
from glob import glob

parser = OptionParser()  # TODO: help
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
    pdfs = read()

    # 2.1 Rotate
    if options.rotations is not None:
        pdfs = [rotate(pdf) for pdf in pdfs]

    # 3 Save
    for filename, pdf in zip(options.filenames, pdfs):
        save((pdf, filename))


def read() -> list:
    """
    Reads PDF file(s) and returns list.
    :return:
    """
    #TODO: glob einführen
    pdfs = []
    for filename in options.filenames:
        with open(filename, "rb") as file:
            pdfs.append(PDF.loads(file))
    return pdfs


def save(*pdf_and_paths):
    """
    Saves pdf to disk.
    :param pdf_and_paths: tuple of len 2: (<pdf>, <filepath>)
    :return:
    """
    for pdf_and_path in pdf_and_paths:
        with open(pdf_and_path[1], "wb") as file:
            PDF.dumps(file, pdf_and_path[0])


def rotate(pdf):
    """
    Syntax:
    Rotate left = Rotate counterclockwiese = L
    twice = LL or RR
    ::2 --> die 1,3,5,...
    1::2 --> die 2,4,6,...
    #TODO umstellen auf: R1-5,7,8 und R2n und H2n+1
    :param pdf:
    :return:
    """

    n = int(pdf.get_document_info().get_number_of_pages())

    for rotation in options.rotations:
        # Determine requested pages for rotation
        all_idx = [False for _ in range(n)]
        sequences = rotation[1:].split(",")
        for seq in sequences:
            seq = seq.strip()
            if seq.isdigit() and 0 <= int(seq)-1 < n:
                all_idx[int(seq)-1] = True
            elif "n" in seq:
                pass
            elif "-" in seq:
                lower, upper = [int(i) for i in seq.split("-")]
                all_idx[lower-1:upper] = [True for _ in range(lower-1, upper)]
        # Apply Rotation
        mode = rotation[0]
        for idx, entry in enumerate(all_idx):
            if entry:
                if mode == "R":
                    pdf.get_page(idx).rotate_right()
                elif mode == "L":
                    pdf.get_page(idx).rotate_left()
                elif mode  == "V":
                    pdf.get_page(idx).rotate_right()
                    pdf.get_page(idx).rotate_right()
    return pdf


def merge(*pdfs):
    pass


if __name__ == "__main__":
    main()


