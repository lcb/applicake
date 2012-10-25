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

from applicake.applications.commons.generator import DatasetcodeGenerator
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

#helper function
def wrap(applic, input_file_name, output_file_name, opts=None):
    argv = ['', '-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    application = applic()
    if isinstance(application, Generator):
        runner = IniFileRunner()
    elif isinstance(application, IApplication):
        runner = ApplicationRunner()
        print 'use application runner'
    elif isinstance(application, IWrapper):
        runner = WrapperRunner()
    else:
        raise Exception('could not identfy runner for application [%s]' % applic.__name__)    
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed with exitcode [%s]" % (applic.__name__, exit_code)) 

def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        subprocess.call("rm *ini* *.err *.out",shell=True)    
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/malars/workflows
LOG_LEVEL = INFO
STORAGE = file
THREADS = 2
DATASET_CODES = 20121002200049906-707790
IRTTRAML = "/cluster/home/biol/loblum/osw/traml/DIA_iRT.TraML"
LIBTRAML = "/cluster/home/biol/loblum/osw/traml/AQUASky_ShotgunLibrary_3t_345_sh.TraML"

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
def generatorDSS(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini', '--GENERATORSIRT', 'generateirt.ini']
    runner = IniFileRunner()
    application = DatasetcodeGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 

@transform(generatorDSS, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata',dir='.')   
    wrap(Dss,input_file_name, output_file_name,['--PREFIX', 'getmsdata','--RESULT_FILE',tfile])


@transform(dss, regex("dss.ini_"), "splitwindows.ini_")
def splitwindows(input_file_name, output_file_name):
    wrap(SplitWindows,input_file_name, output_file_name) 

@follows(splitwindows)
@split('splitwindows.ini_*', "generatesplits.ini_*")
def generatorWindows(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini', '--GENERATORSIRT', 'generateirt.ini']
    runner = IniFileRunner()
    application = SplitGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code)       
################## iRT BRANCH #################################

@transform(generatorWindows, regex("generateirt.ini_"), "chromatogramextractorirt.ini_")
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
    wrap(FileMerger, 'unifier.ini', 'filemerger.ini',['-s','file'])     
    
@follows(filemerger)
def mrmrtnormalizer():
    wrap(MRMRTNormalizer, 'filemerger.ini', 'mrmrtnormalizer.ini')

################## AQUA BRANCH, REQUIRES IRT IN KEYEXTRAT#####################
  
@transform(generatorWindows, regex("generate.ini_"), "cromatogramextractor.ini_")
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

    
#pipeline_run([featurexmltotsv],multiprocess=8,verbose=2)
pipeline_printout_graph ('flowchart.png','png',[featurexmltotsv])