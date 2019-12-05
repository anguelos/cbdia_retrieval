import pathlib
import pickle
import os
from .page import Page
from .util import json_load_np, json_save_np


class PageRegions(object):
    @classmethod
    def load_external(cls, page_filename, ltrb, region_type):
        path = pathlib.Path(page_filename)
        book_id, page_num, md5 = path.stem.split("_")
        book_id = int(book_id)
        page_num = int(page_num)
        book_root = path.parent
        return cls(ltrb=ltrb, book_id=book_id, page_num=page_num, book_root=book_root, md5=md5, region_type=region_type)

    @classmethod
    def load(cls, filename, page=None):
        path = pathlib.Path(filename)
        if pathlib.Path(filename).suffix == ".json":
            ltrb = json_load_np(filename)
        elif pathlib.Path(filename).suffix == ".pickle":
            ltrb = pickle.load(open(filename))
        else:
            raise ValueError("Unrecognised region file type")

        book_id, page_num, md5, region_type = path.stem.split("_")
        book_id = int(book_id)
        page_num = int(page_num)
        book_root = path.parent
        return cls(ltrb=ltrb, book_id=book_id, page_num=page_num, book_root=book_root, md5=md5, region_type=region_type,
                   page=page)

    def __init__(self, ltrb, book_id, page_num, book_root, md5, region_type, page=None):
        self._page = page
        self.ltrb = ltrb
        self.book_id = book_id
        self.page_num = page_num
        self.book_root = book_root
        self.md5 = md5
        self.region_type = region_type
        self.binary_io = False

    def __getitem__(self, item):
        l, t, r, b = self.ltrb[item, :]
        return l, t, r, b

    def __len__(self):
        return self.ltrb.shape[0]

    @property
    def page_filename(self):
        return os.path.join(self.book_root, "{:07d}_{:06d}_{}.png".format(self.book_id, self.page_num, self.md5))

    @property
    def page(self):
        if self._page is None:
            self._page = Page.load(self.page_filename)
        return self._page

    @property
    def id(self):
        return "{:07d}_{:06d}_{}_{}".format(self.book_id, self.page_num, self.md5, self.region_type)

    @property
    def filename(self):
        if self.binary_io:
            return self.get_binary_filename()
        else:
            return self.get_text_filename()

    def get_all_items(self):
        return [self[n] for n in range(self.ltrb.shape[0])]

    def save(self):
        if self.binary_io:
            self.save_binary()
        else:
            self.save_text()

    def save_binary(self):
        pickle.dump(self.ltrb, open(self.get_binary_filename(), "w"))

    def save_text(self):
        json_save_np(self.ltrb, self.get_text_filename())

    def get_binary_filename(self):
        return os.path.join(self.book_root, self.id+".pickle")

    def get_text_filename(self):
        return os.path.join(self.book_root, self.id+".json")
