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
            f.write("""BASEDIR = /cluster/scratch_xp/shareholder/imsb_ra/workflows
SPACE = ROSETTA
PROJECT = DECOYS
OUTEXPERIMENT = DECOYS
LOG_LEVEL = DEBUG
STORAGE = unchanged
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DATASET_CODE = 20130528220101400-821432, 20130528220121441-821433, 20130528220557246-821474, 20130528220622499-821487

WORKFLOW = ruffus_local_rosetta
COMMENT = comment
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox

N_MODELS = 2
RANDOM_GROW_LOOPS_BY = 4
SELECT_BEST_LOOP_FROM = 1""")


@follows(setup)
@files("input.ini", "jobidx.ini")
def jobidx(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/rosetta/jobid.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@follows(jobidx)
@split("jobidx.ini", "split.ini_*")
def split(infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/split.py',
                           '--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'DATASET_CODE'])


@transform(split, regex("split.ini_"), "dss.ini_")
def dss(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/dss.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--EXECUTABLE', 'getdataset'])


@transform(dss, regex("dss.ini_"), "extractrosetta.ini_")
def extractrosetta(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/rosetta/extractrosetta.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@transform(extractrosetta, regex("extractrosetta.ini_"), "rosetta.ini_")
def rosetta(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/rosetta/rosetta.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@transform(rosetta, regex("rosetta.ini_"), "cp2dropbox.ini_")
def copy2rosettadropbox(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/rosetta/dropbox.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


pipeline_run([copy2rosettadropbox], multiprocess=6)