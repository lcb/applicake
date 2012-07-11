#!/usr/bin/env python
'''
Created on Jul 11, 2012

@author: quandtan
'''



import os
import sys
from ruffus import *
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.runner import IniFileRunner2, ApplicationRunner,CollectorRunner,WrapperRunner, IniFileRunner

from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.openswath.chromatogramextractor import ChromatogramExtractor
from applicake.applications.proteomics.openswath.mrmnormalizer import MRMNormalizer
from applicake.applications.proteomics.openswath.mrmanalyzer import MRMAnalyzer

cwd = None


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

def execute(command):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
    output, error = p.communicate()                                                                                                                                                                            
    out_stream = StringIO(output)
    err_stream = StringIO(error) 


def setup():
    cwd = '.'
    os.chdir(cwd)
    execute("find . -type d -iname '[0-9]*' -exec rm -rf {} \;")
    execute('rm *.err')
    execute('rm *.out')
    execute('rm *.log')
    execute('rm *ini*')
#    execute('rm jobid.txt') 
    execute('rm flowchart.*')    
    with open("input.ini", 'w+') as f:
        f.write("""BASEDIR = /cluster/home/biol/quandtan/test/workflows
LOG_LEVEL = DEBUG
STORAGE = file
TEMPLATE = template.tpl
THREADS = 4
MZMLGZ = /cluster/scratch/malars/openswath/data/UPS12/data/chludwig_L110830_23_SW/split_chludwig_L110830_23_SW-UPS2_A_SWATH_0.mzML.gz
MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95
MIN_COVERAGE = 0.6
""" 
     
)       
        

@follows(setup)
def chromatogramextractor():
    wrap(ChromatogramExtractor,'input.ini','chromatogramextractor.ini',['-p']) 
    
@follows(chromatogramextractor)
def mrmnormalizer():
    wrap(MRMNormalizer,'chromatogramextractor.ini','mrmnormalizer.ini',['-p'])     

@follows(mrmnormalizer)
def chromatogramextractor2():
    wrap(ChromatogramExtractor,'chromatogramextractor.ini','chromatogramextractor2.ini',['-p']) 

@follows(chromatogramextractor2)
def mrmanalyzer():
    wrap(MRMAnalyzer,'chromatogramextractor2.ini','mrmanalyzer.ini',['-p']) 
      

pipeline_run([mrmanalyzer], multiprocess = 4)

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
