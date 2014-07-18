#!/usr/bin/env python
import os
import sys
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
BASEDIR = /cluster/scratch_xp/shareholder/imsb_ra/workflows
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox

LOG_LEVEL = INFO
STORAGE = unchanged
WORKFLOW = traml_create

EXPERIMENT = E287786
DATASET_CODE = 20120320163951515-361883, 20120320163653755-361882, 20120320164249179-361886
PEPTIDEFDR = 0.01

COMMENT = newUPS1
DESCRIPTION = newUPS measurement 3 technical replicates
MS_TYPE = CID-QTOF

RSQ_THRESHOLD = 0.95
RTKIT = 
APPLYCHAUVENET = False
PRECURSORLEVEL = False
SPECTRALEVEL = False
TSV_MASS_LIMITS = 400-2000
TSV_ION_LIMITS = 2-6
TSV_PRECISION = 0.05
TSV_CHARGE = 1;2
TSV_REMOVE_DUPLICATES = True 
TSV_EXACT = False
TSV_GAIN =  
TSV_SERIES = 
CONSENSUS_TYPE = Consensus
RUNRT = True

""")

@follows(setup)
@files('input.ini', 'getexperiment.ini')
def getexperiment(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/dss.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--EXECUTABLE', 'getexperiment'])
@follows(getexperiment)
@files('getexperiment.ini', 'processexperiment.ini')
def processexperiment(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/processexperiment.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


################################################################################################

@follows(processexperiment)
@split('processexperiment.ini', "split.ini_*")
def split_dataset(infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/split.py',
                           '--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'DATASET_CODE'])


@transform(split_dataset, regex("split.ini_"), "dss.ini_")
def dss(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/dss.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--EXECUTABLE', 'getmsdata'])


@merge(dss, "mergedataset.ini_0")
def merge_dataset(unused_infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/merge.py',
                           '--MERGE', 'dss.ini', '--MERGED', 'mergedataset.ini'])


################################################################################################

@follows(merge_dataset)
@files("mergedataset.ini_0", "raw.ini")
def rawlib(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/libcreation/spectrastraw.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

#########OPTIONAL################

@follows(rawlib)
@files("raw.ini", "calib.ini")
def irtcalibration(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/libcreation/spectrastirtcalib.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@follows(irtcalibration)
@files("calib.ini", "noirt.ini")
def noirt(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/libcreation/spectrastnoirt.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

#########DONE BY DEFAULT########################

@follows(noirt)
@files("noirt.ini", "totraml.ini")
def totraml(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/libcreation/spectrast2tsv2traml.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

@follows(totraml)
@files("totraml.ini", "cp2dropbox.ini")
def cp2dropbox(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/libcreation/dropbox.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


pipeline_run([cp2dropbox], multiprocess=3)
