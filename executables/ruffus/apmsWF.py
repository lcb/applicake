#!/usr/bin/env python
import sys
import os
import subprocess

from ruffus import *


basepath = os.path.dirname(__file__) + '/../../'

def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'cont':
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    else:
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.log", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox

LOG_LEVEL = DEBUG
WORKFLOW = ruffus_apms
COMMENT = ruffus_apms_comment

EXPERIMENT = E1401171608
DATASET_CODE = 20130729145922792-841677, 20130729155525874-841729, 20130729163423281-841745, 20130729162326487-841742, 20130729162327816-841743, 20130729153430766-841715, 20130729162323826-841741, 20130729154425101-841722, 20130729155623876-841731, 20130729145825371-841676, 20130729151122281-841692, 20130729162422452-841744
IPROB = 0.901
COMPPASS_CONFIDENCE = 0.951

SPACE = LOBLUM
PROJECT = JUNK
OUTEXPERIMENT = EAPMS
""")


@follows(setup)
@files('input.ini', 'getexperiment.ini')
def getexperiment(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/dss.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--EXECUTABLE', 'getexperiment'])


@follows(getexperiment)
@files('getexperiment.ini', 'readexpprop.ini')
def readexpprop(infile, outfile):
    subprocess.check_call(['python', basepath +'appliapps/apms/processexpms.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@follows(readexpprop)
@files('readexpprop.ini', 'assoc.ini')
def doassoc(infile, outfile):
    subprocess.check_call(['python', basepath +'appliapps/apms/getannot.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@follows(doassoc)
@files('assoc.ini', 'apms.ini')
def doapms(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/apms/apmsr.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@follows(doapms)
@files('apms.ini', 'cp2box.ini')
def copy2box(infile, outfile):
    subprocess.check_call(['python', basepath +'appliapps/apms/dropbox.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


if __name__ == "__main__":
    pipeline_run([copy2box])
