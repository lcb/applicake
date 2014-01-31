#!/usr/bin/env python
'''
Created on Oct 18, 2012

@author: quandtan, loblum
'''

import sys
import subprocess
import tempfile

from ruffus import *
from applicake.applications.proteomics.apms.apms import Apms
from applicake.applications.proteomics.apms.apmsdropbox import Copy2ApmsDropbox
from applicake.applications.proteomics.apms.getannot import GetAnnotations
from applicake.applications.proteomics.apms.processexperimentapms import ProcessExperimentApms
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.libcreation.libcreatedropbox import Copy2LibcreateDropbox


#helper function
def wrap(applic, input_file_name, output_file_name, opts=None):
    argv = ['-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    application = applic()
    if isinstance(application, IApplication):
        runner = IniApplicationRunner()
    elif isinstance(application, IWrapper):
        runner = IniWrapperRunner()
    else:
        raise Exception('could not identfy runner for [%s]' % applic.__name__)
    application = applic()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % (applic.__name__, exit_code))


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.err *.out", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox

LOG_LEVEL = DEBUG
STORAGE = unchanged
WORKFLOW = ruffus_apms
COMMENT = ruffus_apms_test
MODULE = imsbtools/20131101

EXPERIMENT = E1401171608
IPROBABILITY = 0.901
COMPPASS_CONFIDENCE = 0.951

SPACE = LOBLUM
PROJECT = JUNK
OUTEXPERIMENT = EAPMS

""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'


@follows(setup)
@files('input.ini', 'getexperiment.ini')
def getexperiment(input_file_name, output_file_name):
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getexperiment'])


@follows(getexperiment)
@files('getexperiment.ini', 'readexpprop.ini')
def readexpprop(input_file_name, output_file_name):
    wrap(ProcessExperimentApms, input_file_name, output_file_name)

@follows(readexpprop)
@files('readexpprop.ini', 'assoc.ini')
def doassoc(input_file_name, output_file_name):
    wrap(GetAnnotations, input_file_name, output_file_name)


@follows(doassoc)
@files('assoc.ini', 'apms.ini')
def doapms(input_file_name, output_file_name):
    wrap(Apms, input_file_name, output_file_name)

@follows(doapms)
@files('apms.ini', 'cp2box.ini')
def copy2box(input_file_name, output_file_name):
    wrap(Copy2ApmsDropbox, input_file_name, output_file_name)

pipeline_run([copy2box], verbose=2)
