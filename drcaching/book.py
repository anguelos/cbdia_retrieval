from .util import log
import multiprocessing
import pathlib
import os
import json
import glob
import numpy as np
import time

from .util import mkdir_p, strtime
from .page import Page
from .regions import PageRegions
from .annotations import PageRegionTranscriptions


def register_wordgt_page(params):
    filename, book_id, page_num, book_root = params
    page = Page.load_external(filename, book_id, page_num, book_root)
    page.save()
    res = page.id
    gt_fname = str(filename)[:-3] + "json"
    if os.path.exists(gt_fname):
        data = json.load(open(gt_fname))
        ltrb = data["rectangles_ltrb"]
        transcriptions = np.array([c[2:] if c[:2] == "W@" else "" for c in data["captions"]])
        regions = PageRegions.load_external(page.get_img_filename(), np.array(ltrb), "gtwords")
        words = PageRegionTranscriptions.load_external(regions.filename,transcriptions)
        words.save()
        regions.save()
    else:
        log(0, "Warning! Groundtruth File ({}) not found".format(gt_fname))
    return res, (page.width, page.height)


def register_page(params):
    filename, book_id, page_num, book_root = params
    page = Page.load_external(filename, book_id, page_num, book_root)
    page.save()
    res = page.id
    return res, (page.width, page.height)


def register_book(book_root, book_id, input_directory, page_pattern, jobs=5, word_boxes_pattern=None,
                  page_register=register_page, title=None, booktype=None, dpi=None, date=None,
                  location=None, writer_id=None):
    """Registers A book into the database.

    :param book_root:
    :param book_id:
    :param input_directory:
    :param page_pattern:
    :param jobs: How many pages to process simultaneously.
    :param word_boxes_pattern:
    :param page_register: The functor that registers the page. Must be one of register_page or register_wordgt_page.
    :param title: A string with the book title or "NA".
    :param booktype: A string with the book title or "NA".
    :param dpi: An integer with the scanning metadata or -1 if unknown.
    :param date: A string with the book creation data or "NA".
    :param location: A string with the book location or "NA".
    :param writer_id: A string with the writer identity or "NA".
    :return: None
    """
    assert page_register in [register_wordgt_page, register_page]
    t = time.time()
    report = "Book Aquisition Log:\n"
    mkdir_p(book_root)
    pages = sorted(list(pathlib.Path(input_directory).glob(page_pattern)))
    if word_boxes_pattern is not None:
        word_boxes = sorted(glob.glob(word_boxes_pattern))
        assert len(word_boxes) == len(pages)
    parameters = [[pages[n], book_id, n, book_root] for n in range(len(pages))]
    if jobs > 1:
        pool = multiprocessing.Pool(jobs)
        ids_sizes = pool.map(register_wordgt_page, parameters)
    else:
        ids_sizes = [register_wordgt_page(p) for p in parameters]
    pixel_count = sum([ids_sizes[n][1][0] * ids_sizes[n][1][1] for n in range(len(ids_sizes))])

    book_metadata = {"pagecount": len(ids_sizes),
                     "pixel_count": pixel_count,
                     "writer_id": writer_id,
                     "date": date,
                     "title": title,
                     "booktype": booktype,
                     "dpi": dpi,
                     "location": location}

    json.dump(book_metadata, open(os.path.join(book_root, "meta.json"), "w"), indent=2)

    report += "Page register:{}\n".format(repr(page_register))
    report += "Metadata:\nt"+"\n\t".join(["{}:{}".format(k, v) for k, v in book_metadata.items()])+"\n"
    report += "Aquisition Start: {}\n".format(strtime(t))
    report += "Aquisition End: {}\n".format(strtime())
    report += "Imported {} files having {:03f} MPixels in {:03f} sec.\n".format(len(ids_sizes),pixel_count/1000000.0,
                                                                                time.time()-t)
    report += "Original Files:\n"+"\n".join(["{}->{}".format(pages[n], ids_sizes[n][0]) for n in range(len(ids_sizes))])

    open(os.path.join(book_root, "acquisition.log"), "w").write(report)

    log(2, report)
