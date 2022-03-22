import numpy as np
import os, sys
import shutil
import glob

all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
print(all_subdirs)
for dirs in all_subdirs:
    all_files = glob.glob(dirs + "/*")
    for file in all_files:
        subdir = os.path.dirname(file)
        filenm = os.path.basename(file)
        shutil.copyfile(file, subdir + "_" + filenm)
