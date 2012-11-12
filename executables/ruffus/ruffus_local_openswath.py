#!/usr/bin/env python
'''
Created on Jul 11, 2012

@author: quandtan, wolski, blum
'''


import sys
import subprocess
import tempfile
from ruffus import *

from applicake.framework.runner import IniFileRunner, IniFileRunner2, IApplication, IWrapper, WrapperRunner, CollectorRunner
from applicake.applications.commons.collector import BasicCollector
from applicake.applications.commons.inifile import Unifier
from applicake.applications.commons.generator import Generator

#workflow specific inputs 
from applicake.applications.commons.generator import DatasetcodeGenerator
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.openswath.splitwindows import SplitWindows
from applicake.applications.proteomics.openswath.mzxmls2mzmls import Mzxmls2Mzmls
from applicake.applications.proteomics.openswath.chromatogramextractor import ChromatogramExtractor, IRTChromatogramExtractor
from applicake.applications.proteomics.openswath.openswathrtnormalizer import OpenSwathRTNormalizer
from applicake.applications.proteomics.openswath.openswathanalyzer import OpenSwathAnalyzer
from applicake.applications.proteomics.openswath.featurexmltotsv import FeatureXMLToTSV
from applicake.applications.proteomics.openswath.mprophet import mProphet


def WrapApp(applic, input_file_name, output_file_name, opts=None):
    argv = ['fakename.py', '-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    
    application = applic()
    
    if isinstance(application, Generator):
        runner = IniFileRunner()
        argv.remove('-o')
        argv.remove('')
    elif isinstance(application, BasicCollector):
        runner = CollectorRunner()
        argv.remove('-i')
        argv.remove('')
    elif isinstance(application, Unifier):
        runner = IniFileRunner2()
    elif isinstance(application, IApplication):
        runner = ApplicationRunner()
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
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
LOG_LEVEL = INFO
STORAGE = memory_all
THREADS = 2
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

DATASET_CODE = 20120713110650516-637617, 20120713110650516-637617
IRTTRAML = "/cluster/home/biol/loblum/oswtraml/DIA_iRT.TraML"
TRAML = "/cluster/home/biol/loblum/oswtraml/AQUASky_ShotgunLibrary_3t_345_sh.TraML"

#DATASET_CODE = 20120815035639258-664552, 20121025182348951-723768
#IRTTRAML = "/cluster/home/biol/loblum/oswtraml/DIA_iRT.TraML"
#TRAML = "/cluster/home/biol/loblum/oswtraml/RCC_kinases.TraML"


MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95, 0.96
MIN_COVERAGE = 0.6
IRTOUTSUFFIX = _rtnorm.chrom.mzML
LIBOUTSUFFIX = .chrom.mzML
""")
    else:
        print 'Continuing'       
        
        
@follows(setup)
@split("input.ini", "dssgenerator.ini_*")
def DSSgenerator(input_file_name, notused_output_file_names):
    WrapApp(DatasetcodeGenerator, input_file_name, '', ['--GENERATORS', 'dssgenerator.ini'])

@transform(DSSgenerator, regex("dssgenerator.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata',dir='.')   
    WrapApp(Dss,input_file_name, output_file_name,['--PREFIX', 'getmsdata','--RESULT_FILE',tfile])


@transform(dss, regex("dss.ini_"), "splitwindows.ini_")
def splitwindows(input_file_name, output_file_name):
    WrapApp(SplitWindows,input_file_name, output_file_name) 

@transform(splitwindows, regex("splitwindows.ini_*"), 'convertmz.ini_')
def convertmz(input_file_name, output_file_name):
    WrapApp(Mzxmls2Mzmls,input_file_name, output_file_name) 


@transform(convertmz, regex("convertmz.ini_*"), "IRTchromatogramextractor.ini_")
def IRTchromatogramextractor(input_file_name, output_file_name):
    WrapApp(IRTChromatogramExtractor, input_file_name, output_file_name,['-n','IRTChromatogramExtractor']) 
       
@transform(IRTchromatogramextractor, regex("IRTchromatogramextractor.ini_*"),"IRTopenswathrtnormalizer.ini_")
def openswathrtnormalizer(input_file_name,output_file_name):
    WrapApp(OpenSwathRTNormalizer, input_file_name,output_file_name)

################## AQUA BRANCH, REQUIRES IRT IN KEYEXTRAT#####################
  
@transform(openswathrtnormalizer, regex("IRTopenswathrtnormalizer.ini_*"), "chromatogramextractor.ini_")
def chromatogramextractor(input_file_name, output_file_name):
    WrapApp(ChromatogramExtractor, input_file_name, output_file_name) 

    
@transform(chromatogramextractor, regex("chromatogramextractor.ini_"), "openswathanalyzer.ini_")
def openswathanalyzer(input_file_name, output_file_name):  
    WrapApp(OpenSwathAnalyzer, input_file_name, output_file_name) 

@transform(openswathanalyzer,regex("openswathanalyzer.ini_"), "featurexml2tsv.ini_")
def featurexmltotsv(input_file_name, output_file_name):
    WrapApp(FeatureXMLToTSV, input_file_name, output_file_name) 

@transform(featurexmltotsv,regex("featurexml2tsv.ini_"), "mprophet.ini_")
def mprophet(input_file_name, output_file_name):
    WrapApp(mProphet, input_file_name, output_file_name) 

#pipeline_run([IRT_merge],multiprocess=4,verbose=2)
pipeline_printout_graph ('flowchart.png','png',[mprophet])
