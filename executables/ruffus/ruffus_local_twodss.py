#!/usr/bin/env python
'''
Created on Aug 15, 2012

@author: loblum
'''
import sys
import subprocess
import tempfile
from ruffus import *
from applicake.applications.proteomics.openbis.processexperiment import ProcessExperiment
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.framework.runner import IniFileRunner2, ApplicationRunner,CollectorRunner,WrapperRunner, IniFileRunner
from applicake.applications.commons.generator import DatasetcodeGenerator,\
    ParametersetGenerator
from applicake.framework.interfaces import IApplication, IWrapper
    
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
WORKFLOW = twodss

EXPERIMENT = E286955
""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    
@follows(setup)
def getexperiment():
     wrap(Dss,'input.ini','getexperiment.ini',['--PREFIX', 'getexperiment'])

@follows(getexperiment)
def processexperiment():
    wrap(ProcessExperiment,'getexperiment.ini','processexperiment.ini',['--GETCODES','True'])

@follows(processexperiment)   
@split('processexperiment.ini', "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini','-o','generator.ini']
    runner = IniFileRunner()
    application = DatasetcodeGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
    
@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata',dir='.')   
    wrap(Dss,input_file_name, output_file_name,['--PREFIX', 'getmsdata','--RESULT_FILE',tfile])
    
pipeline_run([dss], multiprocess=16)