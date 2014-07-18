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
            WORKFLOW = sequest_import_ruffus
SEQUESTHOST = 1
SEQUESTRESULTPATH = 475
PEPTIDEFDR = 0.01
IPROPHET_ARGS = MINPROB=0
LOG_LEVEL = DEBUG
STORAGE = unchanged
BASEDIR = /cluster/scratch_xp/shareholder/imsb_ra/workflows/
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/drop-box_prot_ident
USERNAME = loblum
DECOY_STRING = DECOY_
SPACE = LOBLUM
PROJECT = JUNK
COMMENT = ruffus sequest WF
""")


@follows(setup)
@split("input.ini", "split.ini_*")
def generator(infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/sequestimport/sequestsplit.py',
                           '--INPUT', infile, '--SPLIT', 'split.ini'])

@transform(generator, regex("split.ini_"), "peppro.ini_")
def peppro(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/peptideprophet.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

@merge(peppro, "mergedatasets.ini")
def merge_datasets(unused_infiles, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/merge.py',
                           '--MERGE', 'peppro.ini', '--MERGED', outfile])

@follows(merge_datasets)
@files("mergedatasets.ini_0", "datasetiprophet.ini")
def datasetiprophet(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/interprophet.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@follows(datasetiprophet)
@files("datasetiprophet.ini", "proteinprophet.ini")
def proteinprophet(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/proteinprophet.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

@follows(proteinprophet)
@files("proteinprophet.ini", "protxml2openbis.ini")
def protxml2openbis(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/protxml2openbis.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

@follows(protxml2openbis)
@files("protxml2openbis.ini", "copy2dropbox.ini")
def copy2dropbox(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/sequestimport/dropbox.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


pipeline_run([copy2dropbox], multiprocess=3)
