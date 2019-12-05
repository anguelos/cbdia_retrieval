import pathlib
import sys
import cv2
import time
import json
import numpy as np


def strtime(t=None):
    if t is None:
        t = time.time()
    return time.asctime(time.localtime(t))


def load_image(filename):
    log(9, "Loading", filename)
    img=cv2.imread(str(filename),cv2.IMREAD_COLOR)
    assert img is not None
    img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    return img


def save_image(filename,img):
    log(9,"Saving",filename)
    cv2.imwrite(str(filename),img)


def mkdir_p(dirname):
    pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)


def log(level, *args, stream=sys.stderr):
    if level < log.log_level:
        msg = " ".join([str(a) for a in args])
        stream.write(msg+"\n")
log.log_level = 3


def json_save_np(np_obj, filename):
    fd = open(filename, "w")
    json.dump(np_obj.tolist(), fd, ensure_ascii=False, indent=2)


def json_load_np(filename):
    fd = open(filename)
    return np.array(json.load(fd, ensure_ascii=False))
