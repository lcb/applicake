#!/usr/bin/env python
'''
Created on Jul 11, 2012

@author: quandtan, wolski, blum
'''


import sys
import subprocess
import tempfile
import shutil
from ruffus import *

from applicake.framework.runner import IniFileRunner, IniFileRunner2, IApplication, IWrapper, WrapperRunner, CollectorRunner,\
    ApplicationRunner
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
from applicake.applications.proteomics.openbis.dropbox import Copy2SwathDropbox

#helper methods
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

        
######################START OF WF##############################

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

@transform(mprophet,regex("featurexml2tsv.ini_"), "mprophet.ini_")
def copytodropbox(input_file_name, output_file_name):
    WrapApp(Copy2SwathDropbox, input_file_name, output_file_name) 
########################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print """Please specify action: continue | writeexampleini | FILENAME        
continue: continue started workflow
writeexampleini: writes built in example.ini
FILENAME: copies FILENAME to input.ini and starts workflow"""
        sys.exit(0)
    elif sys.argv[1] == 'writeexampleini':
        print "Writing example.ini"
        with open("example.ini", 'w+') as f:
                f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
LOG_LEVEL = INFO
STORAGE = memory_all
THREADS = 1
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

IRTTRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_DIA_iRT.TraML"

DATASET_CODE = 20120713110650516-637617
TRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_AQUASky_ShotgunLibrary_3t_345_sh.TraML"
#DATASET_CODE = 20120815035639258-664552, 20121025182348951-723768
#TRAML = "/cluster/home/biol/loblum/oswtraml/guot_RCC_cells_PP09_iRTcal_consensus.TraML"


MIN_UPPER_EDGE_DIST = 1

MIN_RSQ = 0.95
MIN_COVERAGE = 0.6

MPR_NUM_XVAL = 5
WRITE_ALL_PG = 1
WRITE_CLASSIFIER = 1

SPACE = LOBLUM
PROJECT = TEST
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openswath/fakedropbox
""")
        sys.exit(0)
    elif sys.argv[1] == 'continue':
        print "Continuing..."
    else:
        infile = sys.argv[1]
        print "Start. Copying %s to input.ini" % infile
        shutil.copyfile(infile,'input.ini')       
    pipeline_run([mprophet],multiprocess=1,verbose=2)
    #pipeline_printout_graph ('flowchart.png','png',[mprophet])

