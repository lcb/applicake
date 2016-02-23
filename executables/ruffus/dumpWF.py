#!/usr/bin/env python
import os
import sys
import subprocess

from ruffus import *

from appliapps.dump.dropbox import Copy2DumpDropbox
from appliapps.dump.dump import Dump
from appliapps.flow.merge import Merge
from appliapps.flow.split import Split
from appliapps.openbis.dss import Dss

basepath = os.path.dirname(__file__) + '/../../'


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'cont':
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    else:
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.log", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""
DATASET_CODE = 20120320164249179-361886,20120320163951515-361883,20120320163653755-361882
WORKFLOW = dumpwf
BASEDIR = /IMSB/sonas/biol_imsb_aebersold_scratch-2/workflows
DATASET_DIR = /IMSB/sonas/biol_imsb_aebersold_scratch-2/datasets/
DROPBOX = /IMSB/sonas/biol_imsb_aebersold_scratch-2/dropbox/staging/
""")


@follows(setup)
@split("input.ini", "split.ini_*")
def generator(infile, unused_outfile):
    sys.argv = ['--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'DATASET_CODE']
    Split.main()


@transform(generator, regex("split.ini_"), "dss.ini_")
def dss(infile, outfile):
    sys.argv = ['--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'DATASET_CODE','--EXECUTABLE', 'getmsdata']
    Dss.main()


@transform(dss, regex("dss.ini_"), "dump.ini_")
def dump(infile, outfile):
    sys.argv = ['--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'DATASET_CODE','--EXECUTABLE', 'getmsdata']
    Dump.main()

@merge(dump, "merge.ini_0")
def merge(unused_infile, unused_outfile):
    sys.argv = ['--MERGE', 'dump.ini', '--MERGED', 'merge.ini']
    Merge.main()

@follows(merge)
@files("merge.ini_0", "dropbox.ini")
def featurealign(infile, outfile):
    sys.argv = [ '--INPUT', infile, '--OUTPUT', outfile]
    Copy2DumpDropbox.main()



pipeline_run([copy2dropbox], multiprocess=1)
