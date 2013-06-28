#!/usr/bin/env python
'''
Created on Jun 5, 2012

@author: quandtan
'''

import os
from ruffus import *
from applicake.applications.proteomics.openbis.dss import Dss

from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner
from applicake.applications.commons.generator import IniDatasetcodeGenerator
from applicake.applications.proteomics.rosetta.rosetta import Rosetta
from applicake.applications.proteomics.rosetta.extractrosetta import Extractrosetta
from applicake.applications.proteomics.rosetta.rosettadropbox import Copy2RosettaDropbox
from applicake.framework.interfaces import IApplication, IWrapper


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
    #subprocess.call("rm *.err *.out *ini* *.log",shell=True)
    if os.path.exists("input.ini"):
        return
    with open("input.ini", 'w+') as f:
        f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
SPACE = ROSETTA
PROJECT = DECOYS
EXPERIMENT = DECOYS
LOG_LEVEL = INFO
STORAGE = unchanged
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DATASET_CODE = 20120301183733088-335945, 20120301154907468-332952
WORKFLOW = ruffus_local_rosetta
COMMENT = comment
NSTRUCT = 2
DROPBOX = ./
RANDOM_GROW_LOOPS_BY = 4
SELECT_BEST_LOOP_FROM = 1 
""")


@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    wrap(IniDatasetcodeGenerator, input_file_name, "output.ini", ['--GENERATOR', 'generate.ini'])


@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getdataset'])


@transform(dss, regex("dss.ini_"), "extractrosetta.ini_")
def extractrosetta(input_file_name, output_file_name):
    wrap(Extractrosetta, input_file_name, output_file_name)


@transform(extractrosetta, regex("extractrosetta.ini_"), "rosetta.ini_")
def rosetta(input_file_name, output_file_name):
    wrap(Rosetta, input_file_name, output_file_name)


@transform(rosetta, regex("rosetta.ini_"), "cp2dropbox.ini_")
def copy2rosettadropbox(input_file_name, output_file_name):
    wrap(Copy2RosettaDropbox, input_file_name, output_file_name)


pipeline_run([copy2rosettadropbox], verbose=5, multiprocess=3)