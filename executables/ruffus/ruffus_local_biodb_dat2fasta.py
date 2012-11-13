#!/usr/bin/env python
'''
Created on Oct 18, 2012

@author: quandtan
'''

import sys
import subprocess
from ruffus import *
from applicake.applications.biodb.downloader import DatDownloader
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.framework.runner import ApplicationRunner, WrapperRunner
    
#helper function
def wrap(applic,  input_file_name, output_file_name,opts=None):
    argv = ['', '-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    application = applic()
    if isinstance(application, IApplication):
        runner = ApplicationRunner()
        print 'use application runner'
    elif isinstance(application, IWrapper):
        runner = WrapperRunner()
    else:
        raise Exception('could not identfy [%s]' % applic.__name__)    
    application = applic()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % (applic.__name__, exit_code)) 
    
def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.err *.out",shell=True)    
        with open("input.ini", 'w+') as f:
            f.write("""
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
LOG_LEVEL = DEBUG
STORAGE = memory_all
WORKFLOW = biodb_dat2fasta
URL_DAT = ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz
""")
#EXPERIMENT = E286955
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    
@follows(setup)
def download():
    argv = ['','-i','input.ini','-o','datdownloader.ini','--STORAGE','memory_all']
    runner = ApplicationRunner()
    app = DatDownloader()
    exit_code = runner(argv, app)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
#    wrap(DatDownloader,'input.ini','datdownloader.ini')


pipeline_run([download], multiprocess=1)