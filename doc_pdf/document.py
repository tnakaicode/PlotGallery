import numpy as np
import matplotlib.pyplot as plt
import json
import sys
import time
import os
import glob
import shutil
import datetime
from linecache import getline, clearcache
from optparse import OptionParser

from reportlab.lib import pdfencrypt, colors
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PIL import Image

width, height = A4
style_R = getSampleStyleSheet()["BodyText"]
style_R.alignment = TA_RIGHT
style_L = getSampleStyleSheet()["BodyText"]
style_L.alignment = TA_LEFT
style_C = getSampleStyleSheet()["BodyText"]
style_C.alignment = TA_CENTER
table_style = TableStyle([
    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
])

import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)


class PDF (object):

    def __init__(self, filename, dirname="./"):
        self.pdf = canvas.Canvas(dirname + filename, pagesize=A4)


class Doc (PDF):

    def __init__(self, filename, dirname="./"):
        super(Doc, self).__init__(filename, dirname)

    def SetTitle(self, title):
        self.pdf.drawString(*coord(-250, 380), title)
        self.pdf.showPage()

    def Save(self):
        self.pdf.save()

    def Page(self):
        self.pdf.showPage()

    def WriteString(self, sxy=[-250, 380], inpt="name"):
        self.pdf.drawString(*coord(*sxy), inpt)

    def SetPng(self, pngfile, loc, size, title=None):
        if title == None:
            title = pngfile.split("/")[-1].split(".")[-2]
        else:
            title = title
        pdf_png(self.pdf, pngfile, title, loc, size)


def coord(x, y, unit=1):
    return (x + width / 2) * unit, (y + height / 2) * unit


def pdf_png(pdf, pngfile, title="name", loc=[-100, 200], size=5.0):
    img = Image.open(pngfile)
    iw, ih = img.size
    pdf.drawInlineImage(
        pngfile, *coord(loc[0], loc[1] + 10), iw / size, ih / size)
    pdf.drawString(*coord(loc[0] + 20, loc[1]), title)


def create_tempdir(flag=1):
    print(datetime.date.today())
    datenm = "{0:%Y%m%d}".format(datetime.date.today())
    dirnum = len(glob.glob("./temp_" + datenm + "*/"))
    if flag == -1 or dirnum == 0:
        tmpdir = "./temp_{}{:03}/".format(datenm, dirnum)
        os.makedirs(tmpdir)
        fp = open(tmpdir + "not_ignore.txt", "w")
        fp.close()
    else:
        tmpdir = "./temp_{}{:03}/".format(datenm, dirnum - 1)
    print(tmpdir)
    return tmpdir


if __name__ == '__main__':
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--flag", dest="flag", default=1, type="int")
    opt, argc = parser.parse_args(argvs)
    print(opt, argc)
    tmpdir = create_tempdir(opt.flag)

    obj = Doc(filename="test.pdf", dirname=tmpdir)
    obj.WriteString(inpt="Title")
    obj.SetPng(pngfile="./img/adobe-pdf.png", loc=[0, 0], size=5.0)
    obj.Save()
