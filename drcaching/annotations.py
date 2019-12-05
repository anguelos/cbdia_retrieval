from .page import Page
from .regions import PageRegions
import pickle
import pathlib
import os
import glob
from .util import json_save_np, json_load_np


class PageRegionTranscriptions(object):
    @classmethod
    def load_external(cls, region_filename, transcriptions):
        path = pathlib.Path(region_filename)
        book_id, page_num, md5, region_type = path.stem.split("_")
        book_id = int(book_id)
        page_num = int(page_num)
        book_root = path.parent
        return cls(transcriptions, book_id=book_id, page_num=page_num, book_root=book_root, md5=md5,
                   region_type=region_type)

    @classmethod
    def load(cls, filename, page=None, regions=None):
        path = pathlib.Path(filename)
        if pathlib.Path(filename).suffix == ".json":
            transcriptions = json_load_np(filename)
        elif pathlib.Path(filename).suffix == ".pickle":
            transcriptions = pickle.load(open(filename))
        else:
            raise ValueError("Unrecognised transcription file type")

        book_id, page_num, md5, region_type, _ = path.stem.split("_")
        book_id = int(book_id)
        page_num = int(page_num)
        book_root = path.parent
        return cls(transcriptions=transcriptions, book_id=book_id, page_num=page_num, book_root=book_root, md5=md5,
                   region_type=region_type, page=page, regions=regions)

    def __init__(self, transcriptions, book_id, page_num, book_root, md5, region_type, page=None, regions=None):
        self._page = page
        self._regions = regions
        self.transcriptions = transcriptions
        self.book_id = book_id
        self.page_num = page_num
        self.book_root = book_root
        self.md5 = md5
        self.region_type = region_type
        self.binary_io = False

    def __getitem__(self, item):
        return self.transcriptions[item]

    def __len__(self):
        return self.transcriptions.shape[0]

    @property
    def regions(self):
        if self._regions is None:
            self._regions = PageRegions.load(self.get_regions_filename())
        return self._regions

    @property
    def page(self):
        if self._page is None:
            self._page = Page.load(self.get_page_filename())
        return self._regions

    @property
    def id(self):
        return "{}_{}_{}_{}_transcription".format(self.book_id, self.page_num, self.md5, self.region_type)

    @property
    def filename(self):
        if self.binary_io:
            return self.get_binary_filename()
        else:
            return self.get_text_filename()

    def save(self):
        if self.binary_io:
            pickle.dump(open(self.get_binary_filename(), "w"), self.transcriptions)
        else:
            json_save_np(self.transcriptions,self.get_text_filename())

    def get_binary_filename(self):
        return os.path.join(self.book_root, self.id+".pickle")

    def get_text_filename(self):
        return os.path.join(self.book_root, self.id+".json")

    def get_regions_filename(self):
        region_id = "{}_{}_{}_{}".format(self.book_id, self.page_num, self.md5, self.region_type)
        return glob.glob(os.path.join(self.book_root, region_id+".*"))[0]

    def get_page_filename(self):
        page_id = "{}_{}_{}".format(self.book_id, self.page_num, self.md5, self.region_type)
        return os.path.join(self.book_root, page_id+".png")
