import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time
import json
import shutil
import urllib.request as urllib2
from optparse import OptionParser

sys.path.append(os.path.join("../"))
from base import plot2d, plot3d

import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)


def uiuc_database(name="dae51"):
    dat_file = "./uiuc_dat/{}.dat".format(name)
    if os.path.exists(dat_file):
        fp = open(dat_file, "r")
        fp_lines = fp.readlines()
    else:
        uiuc_url = 'http://m-selig.ae.illinois.edu/ads/coord_seligFmt/'
        foil_dat_url = uiuc_url + '{}.dat'.format(name)
        fp = urllib2.urlopen(foil_dat_url)
        fp_lines = fp.readlines()
        qp = open(dat_file, "w")
        for line in fp_lines:
            txt = ""
            dat = line.split()
            for t in dat:
                txt += str(t.decode("utf-8")) + "\t"
            qp.write(txt + "\n")

    data = []
    for idx, line in enumerate(fp_lines[1:]):
        data.append([float(v) for v in line.split()])
    return np.array(data)


if __name__ == '__main__':
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--dir", dest="dir", default="./")
    parser.add_option("--name", dest="name", default="dae51")
    opt, argc = parser.parse_args(argvs)
    print(opt, argc)

    obj = plot2d(aspect="equal")
    cfg = json.load(open("./cfg.json", "r"))
    dat_name = opt.name
    data = uiuc_database(dat_name)
    print(dat_name, data.shape)
    obj.axs.plot(data[:, 0], data[:, 1])
    obj.axs.set_title(dat_name)
    obj.SavePng("./uiuc_dat/{}.png".format(dat_name))
