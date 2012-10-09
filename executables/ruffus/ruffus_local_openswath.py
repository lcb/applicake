#!/usr/bin/env python
'''
Created on Jul 11, 2012

@author: quandtan, wolski, blum
'''

import os
import sys
import subprocess
from ruffus import *

from applicake.framework.interfaces import IApplication, IWrapper
from applicake.framework.runner import ApplicationRunner, CollectorRunner, WrapperRunner, IniFileRunner, IniFileRunner2
from applicake.applications.proteomics.openswath.chromatogramextractor import ChromatogramExtractor
from applicake.applications.proteomics.openswath.mrmrtnormalizer import MRMRTNormalizer
from applicake.applications.proteomics.openswath.mrmanalyzer import MRMAnalyzer
from applicake.applications.proteomics.openswath.featurexmltotsv import FeatureXMLToTSV
from applicake.applications.proteomics.openswath.FileMerger import FileMerger
from applicake.applications.proteomics.openswath.SwathGenerator import SwathGenerator
from applicake.applications.proteomics.openswath.KeyExtract import KeyExtract
from applicake.applications.commons.collector import GuseCollector
from applicake.applications.commons.inifile import Unifier
from applicake.framework.enums import KeyEnum

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
    


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        subprocess.call("rm *ini* *.err *.out",shell=True)    
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/malars/workflows
LOG_LEVEL = DEBUG
STORAGE = file
THREADS = 8
MZMLGZDIR = /cluster/scratch_xl/shareholder/malars/quandtan/openswathtest/datasets3/
LIBTRAML = "/cluster/scratch_xl/shareholder/malars/quandtan/openswathtest/tramls/AQUA4_sh_new.TraML"
IRTTRAML = "/cluster/scratch_xl/shareholder/malars/quandtan/openswathtest/tramls/DIA_iRT.TraML"
MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95
MIN_COVERAGE = 0.6
IRTOUTSUFFIX = _rtnorm.chrom.mzML
LIBOUTSUFFIX = .chrom.mzML
""")
    else:
        print 'Continuing'       
        
@follows(setup)
@split("input.ini", "generate*")
def generator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini', '--GENERATORSIRT', 'generateirt.ini']
    runner = IniFileRunner()
    application = SwathGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
   
################## iRT BRANCH #################################

@transform(generator, regex("generateirt.ini_"), "chromatogramextractorirt.ini_")
def chromatogramExtractorIRT(input_file_name, output_file_name):
    wrap(ChromatogramExtractor, input_file_name, output_file_name,['-n','ChromatogramExtractoriRT']) 

@merge(chromatogramExtractorIRT,'collector.ini')
def collector(notused_input_file_names, output_file_name):
    argv = ['', '--COLLECTORS', 'chromatogramextractorirt.ini', '-o', output_file_name,'-s','file']
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("collector failed [%s]" % exit_code)
    
@follows(collector)
def unifier():
    argv = ['', '-i', 'collector.ini', '-o','unifier.ini','--UNIFIER_REDUCE','-s','file','--LISTS_TO_REMOVE',KeyEnum.FILE_IDX]
    runner = IniFileRunner2()
    application = Unifier()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("unifier failed [%s]" % exit_code)  
    
    
    
@follows(unifier)
def filemerger():
    wrap(FileMerger, 'unifier.ini', 'filemerger.ini',['-s','memory_all'])
    
@follows(filemerger)
def mrmrtnormalizer():
    wrap(MRMRTNormalizer, 'filemerger.ini', 'mrmrtnormalizer.ini')

################## AQUA BRANCH, REQUIRES IRT IN KEYEXTRAT#####################
  
@transform(generator, regex("generate.ini_"), "cromatogramextractor.ini_")
def chromatogramExtractor(input_file_name, output_file_name):
    wrap(ChromatogramExtractor, input_file_name, output_file_name) 

@transform([chromatogramExtractor,mrmrtnormalizer], regex("cromatogramextractor.ini_"), "keyextract.ini_")
def keyextract(input_file_name, output_file_name):
    wrap(KeyExtract, input_file_name, output_file_name, ['--KEYFILE','mrmrtnormalizer.ini','--KEYSTOEXTRACT','TRAFOXML']) 

@transform([keyextract,], regex("keyextract.ini_"), "mrmanalyzer.ini_")
def mrmanalyzer(input_file_name, output_file_name):  
    wrap(MRMAnalyzer, input_file_name, output_file_name) 

@transform(mrmanalyzer,regex("mrmanalyzer.ini_"), "featurexml2tsv.ini_")
def featurexmltotsv(input_file_name, output_file_name):
    wrap(FeatureXMLToTSV, input_file_name, output_file_name,['-p']) 

    
pipeline_run([featurexmltotsv],multiprocess=15,verbose=2)
