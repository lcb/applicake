#!/usr/bin/env python
import os
import shutil
from applicake.app import BasicApp


class RTforward(BasicApp):
    @classmethod
    def main(cls):
        print os.listdir(".")

        if "RUNRT = True" in open("uncalib.ini_0").read():
            print "RUNRT WAS SET TRUE. TRYING TO CONTINUE USING RT-CALIBRATED INPUT"
            try:
                shutil.copy("rtcalib.ini_0", "output.ini")
            except Exception, e:
                raise RuntimeError("cannot copy rtcalibrated input. probably error happened before. "+e.message)
        else:
            print "RUNRT WAS SET FALSE. TRYING TO CONTINUE USING NON-CALIBRATED INPUT"
            shutil.copy("uncalib.ini_0", "output.ini")
