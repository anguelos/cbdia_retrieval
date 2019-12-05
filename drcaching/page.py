#!/usr/bin/env python3
import hashlib
import os
import pathlib
from .util import load_image, save_image


class Page(object):
    @classmethod
    def load_external(cls, filename, book_id=1, page_num=1, book_root="/tmp/bookroot"):
        img = load_image(filename)
        res = cls(img=img, book_id=book_id, book_root=book_root, page_num=page_num)
        return res

    @classmethod
    def load(cls, filename):
        path = pathlib.Path(filename)
        img = load_image(filename)
        book_id, page_num, md5 = path.stem.split("_")
        book_id = int(book_id)
        page_num = int(page_num)
        book_root = path.parent
        return cls(img=img, book_id=book_id, page_num=page_num, book_root=book_root, md5=None)

    def __init__(self, img, book_id, page_num, book_root, md5=None):
        if md5 is None:
            self.md5 = hashlib.md5(img).hexdigest()
        else:
            self.md5 = md5
        self.img = img
        self.book_id = book_id
        self.page_num = page_num
        self.book_root = book_root

    @property
    def width(self):
        return self.img.shape[1]

    @property
    def height(self):
        return self.img.shape[0]

    @property
    def id(self):
        return "{:07d}_{:06d}_{}".format(self.book_id, self.page_num, self.md5)

    def get_img_filename(self):
        return os.path.join(self.book_root, self.id+".png")

    def get_sz_filename(self):
        return os.path.join(self.book_root, self.id+".png")

    def save(self):
        save_image(self.get_img_filename(), self.img)
        open(self.get_sz_filename(), "w").write("{}\t{}\t{}".format(self.get_img_filename(), self.width, self.height))
