#!/usr/bin/env python
import os
import shutil

if __name__ == "__main__":
    print os.listdir(".")

    if "RUNRT = True" in open("uncalib.ini_0").read():
        print "RUNRT WAS SET TRUE. TRYING TO CONTINUE USING RT-CALIBRATED INPUT"
        shutil.copy("rtcalib.ini_0", "output.ini")
    else:
        print "RUNRT WAS SET FALSE. TRYING TO CONTINUE USING NON-CALIBRATED INPUT"
        shutil.copy("uncalib.ini_0", "output.ini")
