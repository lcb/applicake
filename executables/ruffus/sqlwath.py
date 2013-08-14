#!/usr/bin/env python
'''
Created on Aug 13, 2012

@author: quandtan
'''

import sys
import subprocess
import tempfile

from ruffus import *


from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner
from applicake.applications.commons.generator import IniDatasetcodeGenerator

from applicake.applications.proteomics.openbis.dss import Dss

from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.sqlwath.mzxml2sql import Mzxml2Sql
from applicake.applications.proteomics.sqlwath.reindex import ReindexMzxml
from applicake.applications.proteomics.sqlwath.sqlwathdropbox import Copy2SqlwathDropbox

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
        subprocess.call("rm *ini* *.err *.out", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""WORKFLOW = ruffus_local_sqlwath
COMMENT = nocomment
DATASET_CODE = 20120713110650516-637617, 20120712234103658-637318
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows/
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox
STORAGE = unchanged
LOG_LEVEL = INFO

SPACE = LOBLUM
PROJECT = TEST
EXPERIMENT = E_SQLWATH

THREADS = 4

MZSCALE = 1.3
RTSCALE = 1.3
RESOLUTION = 35000
MASSRANGE = 400-600
MZWIDTH = 9
RTWIDTH = 9
MININTENSITY = 15
""")


@follows(setup)
@split("input.ini", "dssgenerator.ini_*")
def DSSgenerator(input_file_name, notused_output_file_names):
    wrap(IniDatasetcodeGenerator, input_file_name, 'dssgenerator.ini', ['--GENERATOR', 'dssgenerator.ini'])
 
@transform(DSSgenerator, regex("dssgenerator.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    _, tfile = tempfile.mkstemp(suffix='.out', prefix='getdataset', dir='.')
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getdataset','--RESULT_FILE', tfile])

@transform(dss, regex("dss.ini_"), "reindex.ini_")
def reindex(input_file_name, output_file_name):
    wrap(ReindexMzxml, input_file_name, output_file_name)

@transform(reindex, regex("reindex.ini_"), "xml2sql.ini_")
def xml2sql(input_file_name, output_file_name):
    wrap(Mzxml2Sql, input_file_name, output_file_name)

@transform(xml2sql, regex("xml2sql.ini_"), "copy2dropbox.ini_")
def copy2dropbox(input_file_name, output_file_name):
    wrap(Copy2SqlwathDropbox, input_file_name, output_file_name)


pipeline_run([copy2dropbox], multiprocess=2)

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
