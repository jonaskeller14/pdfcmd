import pikepdf
from optparse import OptionParser
from glob import glob
import os
import logging
import sys


def main():
    # READ -----------------------------------------------------------------------------------------------------------
    logging.info("Reading...")
    pdfs, filenames = read()
    for filename in filenames:
        logging.info("\t" + filename)
        if options.open:
            os.system(f'start chrome "{os.path.abspath(filename)}"')

    del_src = False
    save_src = False if not options.remove_password else True

    # 1 ROTATE ---------------------------------------------------------------------------------------------------------
    if options.rotate is not None:
        logging.info("Rotating...")
        pdfs = [rotate(pdf) for pdf in pdfs]
        save_src = True

    # 2 SPLIT ----------------------------------------------------------------------------------------------------------
    if options.split is not None:
        logging.info("Splitting...")
        for pdf, filename in zip(pdfs, filenames):
            split_pdfs = split(pdf)
            for split_idx, split_pdf in enumerate(split_pdfs):
                new_filename = f"{filename[:-4]}_{(split_idx+1):02}.pdf"
                logging.info(f"\t{new_filename}")
                save((split_pdf, new_filename))
        del_src = True

    # 3 EXTRACT --------------------------------------------------------------------------------------------------------
    if options.extract is not None:
        logging.info("Extracting pages...")
        for pdf, filename in zip(pdfs, filenames):
            extract_pdf = extract(pdf)
            new_filename = f"{filename[:-4]}_extract.pdf"
            logging.info(f"\t{new_filename}")
            save((extract_pdf, new_filename))
        del_src = False

    # 4 DELETE ---------------------------------------------------------------------------------------------------------
    if options.delete is not None:
        logging.info("Deleting pages...")
        for idx, pdf in enumerate(pdfs):
            pdfs[idx] = delete(pdf)
        save_src = True

    # 5 MERGE ----------------------------------------------------------------------------------------------------------
    if options.merge is not None:
        logging.info("Merging...")
        logging.info(f"\t{options.merge}")
        pdf_merge = merge(pdfs)
        save((pdf_merge, options.merge))

    # SAVE -----------------------------------------------------------------------------------------------------------
    if save_src:
        logging.info("Saving...")
        for filename, pdf in zip(filenames, pdfs):
            if options.interactive and input(f"Save/Overwrite '{filename}'? [y/n] ") != "y":
                continue
            logging.info(f"\t{filename}")
            save((pdf, filename))
            if options.open:
                os.system(f'start chrome "{os.path.abspath(filename)}"')
    if del_src:
        logging.info("Deleting initial file(s)...")
        for filename in filenames:
            if options.interactive and input(f"Delete '{filename}'? [y/n] ") != "y":
                continue
            logging.info(f"\t{filename}")
            os.remove(filename)


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
            tmp_filenames = sorted(glob(filename))
            filenames += tmp_filenames
            if len(tmp_filenames) == 0:
                logging.warning(f"\tNo files found for '{filename}'")

    # Read pdfs
    pdfs = []
    for filename in filenames:
        if options.interactive and input(f"Read '{filename}'? [y/n] ") != "y":
            continue

        if options.password is None:
            pdfs.append(pikepdf.Pdf.open(filename, allow_overwriting_input=True))
        else:
            pdfs.append(pikepdf.Pdf.open(filename, allow_overwriting_input=True, password=options.password))
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
    :param pdf:
    :return:
    """
    n = len(pdf.pages)

    # Determine requested pages for rotation
    sequences = options.rotate.split(",")
    mode = None
    for seq in sequences:
        # mode
        if seq[0] in ("R", "L", "V"):
            mode = seq[0]
            seq = seq[1:]
        elif mode is None:
            logging.critical("No rotation mode given")
            sys.exit(1)

        # pages
        all_idx = [False for _ in range(n)]
        if seq.strip().isdigit() and 0 <= int(seq.strip())-1 < n:
            all_idx[int(seq)-1] = True
        elif "n" in seq:
            raise NotImplementedError  # TODO
        elif "-" in seq:
            lower, upper = [int(digit.strip()) for digit in seq.split("-")]
            all_idx[lower-1:upper] = [True for _ in range(lower-1, upper)]

        # Apply Rotation
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


def delete(pdf):
    """
    :param pdf:
    :return:
    """
    n = len(pdf.pages)
    all_idx = [False for _ in range(n)]

    # Determine requested pages for rotation
    for seq in options.delete.split(","):
        seq = seq.strip()
        if seq.isdigit() and 0 <= int(seq) - 1 < n:
            all_idx[int(seq) - 1] = True
        elif "n" in seq:
            raise NotImplementedError  # TODO
        elif len(seq.split("-")) == 2:
            lower, upper = [i for i in seq.split("-")]
            if upper == "" and lower != "":
                lower = int(lower)
                all_idx[lower-1:] = [True for _ in range(lower-1, n)]
            elif lower == "" and upper != "":
                upper = int(upper)
                all_idx[:upper] = [True for _ in range(upper)]
            else:
                lower, upper = int(lower), int(upper)
                all_idx[lower-1:upper] = [True for _ in range(lower - 1, upper)]

    # Apply Deletion
    for idx, value in enumerate(reversed(all_idx)):
        if value:
            del pdf.pages[n-1-idx]
    return pdf


def extract(pdf):
    """
    :param pdf:
    :return:
    """
    n = len(pdf.pages)
    all_idx = [False for _ in range(n)]

    # Determine requested pages for extraction
    for seq in options.extract.split(","):
        seq = seq.strip()
        if seq.isdigit() and 0 <= int(seq) - 1 < n:
            all_idx[int(seq) - 1] = True
        elif "n" in seq:
            raise NotImplementedError  # TODO
        elif len(seq.split("-")) == 2:
            lower, upper = [i for i in seq.split("-")]
            if upper == "" and lower != "":
                lower = int(lower)
                all_idx[lower-1:] = [True for _ in range(lower-1, n)]
            elif lower == "" and upper != "":
                upper = int(upper)
                all_idx[:upper] = [True for _ in range(upper)]
            else:
                lower, upper = int(lower), int(upper)
                all_idx[lower-1:upper] = [True for _ in range(lower - 1, upper)]

    # Apply extraction
    new_pdf = pikepdf.Pdf.new()
    for idx, value in enumerate(all_idx):
        if value:
            new_pdf.pages.append(pdf.pages[idx])
    return new_pdf


def merge(pdfs):
    """
    Merges multiple pdfs. Meta-data will be lost.
    :param pdfs: pdf objects
    :return: one pdf object containing all input pdf-pages
    """
    pdf_merge = pikepdf.Pdf.new()
    for pdf in pdfs:
        pdf_merge.pages.extend(pdf.pages)
    return pdf_merge


def split(pdf):
    """
    Example pdf with 5 pages:
    "2" -> [1-2, 3-5]
    "2,4" -> [1-2,3-4,5]
    "n" -> split to single page pdf [1,2,3,4,5]
    "2*n" -> [1-2,3-4,5]
    "2*n+1" -> [1,2-3,4-5]
    :param pdf:
    :param filename:
    :return:
    """
    # Determine split indices
    n = len(pdf.pages)
    split_idx = []
    for seq in options.split.split(","):
        if "n" not in seq:
            split_idx.append(int(seq)-1)
        else:
            res = 1
            i = 0
            while True:
                res = eval(seq.replace("n", str(i))) - 1
                if res < n and res >= 0:
                    split_idx.append(res)
                    i += 1
                elif abs(res) < n:
                    i += 1
                else:
                    break
    # Split pdf
    split_pdfs = []
    new_pdf = pikepdf.Pdf.new()
    for idx, page in enumerate(pdf.pages):
        new_pdf.pages.append(page)
        if idx in split_idx:
            split_pdfs.append(new_pdf)
            new_pdf = pikepdf.Pdf.new()
    if len(new_pdf.pages) > 0:
        split_pdfs.append(new_pdf)
    return split_pdfs


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-10s: %(message)s",
        handlers=[logging.StreamHandler()]
    )

    parser = OptionParser("Script to modify pdf-files (rotate, extract, delete pages, etc.).")
    parser.add_option("-f", "--files",              action="append",    type="string",  dest="filenames",       help="Filepaths of files to be modified.")
    parser.add_option("-o", "--open",               action="store_true",                dest="open",            help="Opens files after process is done.")
    parser.add_option("-i", "--interactive",        action="store_true",                dest="interactive",     help="Ask before each operation")

    parser.add_option("-r", "--rotate",             action="store",     type="string",  dest="rotate",          help="Direction and Page-numbers to be rotated (e.g. for 90°-clockwise 'R2-4,5').")
    parser.add_option("-d", "--delete",             action="store",     type="string",  dest="delete",          help="Page-numbers to be deleted (e.g. '2-4,5').")
    parser.add_option("-m", "--merge",              action="store",     type="string",  dest="merge",           help="Output-Path of merged-pdf. All 'files' will be merged into one.")
    parser.add_option("-e", "--extract",            action="store",     type="string",  dest="extract",         help="Page-numbers to be extracted (e.g. '2-4,5').")
    parser.add_option("-s", "--split",              action="store",     type="string",  dest="split",           help="Page-numbers after initial pdf will be splitted (e.g. for '2', pdf will be split between 2nd and 3rd page).")
    parser.add_option("-p", "--password",           action="store",     type="string",  dest="password",        help="Supply Password for protected files.")
    parser.add_option(      "--remove-password",    action="store_true",                dest="remove_password", help="Remove password.")
    options, args = parser.parse_args()

    main()
