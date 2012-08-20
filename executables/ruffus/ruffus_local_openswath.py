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
from applicake.framework.runner import IniFileRunner2, ApplicationRunner, CollectorRunner, WrapperRunner, IniFileRunner

from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.openswath.chromatogramextractor import ChromatogramExtractor
from applicake.applications.proteomics.openswath.mrmrtnormalizer import MRMRTNormalizer
from applicake.applications.proteomics.openswath.mrmanalyzer import MRMAnalyzer
from applicake.applications.proteomics.openswath.featurexmltotsv import FeatureXMLToTSV
from applicake.applications.proteomics.openswath.FileMerger import FileMerger
from applicake.applications.proteomics.openswath.KeySwitcher import KeySwitcher
from applicake.applications.proteomics.openswath.SwathGenerator import SwathGenerator

cwd = None


#helper function
def wrap(applic, input_file_name, output_file_name, opts=None):
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
        f.write("""BASEDIR = /cluster/home/biol/wwolski/imsb/ruffus
LOG_LEVEL = DEBUG
STORAGE = memmory_all
THREADS = 8
MZMLGZDIR = /cluster/scratch/malars/openswath/data/AQUA_fixed_water/split_napedro_L120224_001_SW-400AQUA_no_background_2ul_dilution_10
CHROMEXTRACTOR1.TRAML = "/cluster/scratch/malars/openswath/assays/iRT/DIA_iRT.TraML"
CHROMEXTRACTOR2.TRAML = "/cluster/scratch/malars/openswath/assays/AQUA/AQUA4_sh.TraML"
MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95
MIN_COVERAGE = 0.6
"""
)       
        
@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini','-o','generator.ini','-l','DEBUG']
    runner = IniFileRunner()
    application = SwathGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 


@transform(generator, regex("generate.ini_"), "chromatogramextractor.ini_")
def chromatogramextractor(input_file_name, output_file_name):
    wrap(ChromatogramExtractor, input_file_name, output_file_name, ['-p']) 


@follows(chromatogramextractor)
def filemerger():
    wrap(FileMerger, 'chromatogramextractor.ini_0', 'filemerger.ini')
    
@follows(filemerger)
def mrmrtnormalizer():
    wrap(MRMRTNormalizer, 'filemerger.ini', 'mrmrtnormalizer.ini', ['-p'])

@follows(mrmrtnormalizer)
def keyswitcher():
    wrap(KeySwitcher, "mrmrtnormalizer.ini", "keyswitcher.ini")

@follows(keyswitcher)
@split("input.ini", "generate2.ini_*")
def generator2(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini','-o','generator.ini','-l','DEBUG']
    runner = IniFileRunner()
    application = SwathGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 

@transform(generator2, regex("generate2.ini_"), "chromatogramextractor2.ini_")
def chromatogramextractor2(input_file_name, output_file_name):
    wrap(ChromatogramExtractor, input_file_name, output_file_name, ['-p']) 

@transform(chromatogramextractor2, regex("chromatogramextractor2.ini_"), "mrmanalyzer.ini_")
def mrmanalyzer(input_file_name, output_file_name):
    wrap(MRMAnalyzer, input_file_name, output_file_name, ['-p']) 

@transform(mrmanalyzer,regex("mrmanalyzer.ini_"), "featurexml2tsv.ini_")
def featurexmltotsv(input_file_name, output_file_name):
    wrap(FeatureXMLToTSV, input_file_name, output_file_name, ['-p']) 

pipeline_run([featurexmltotsv], multiprocess=1)

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
