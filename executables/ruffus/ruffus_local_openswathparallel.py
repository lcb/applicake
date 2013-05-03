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
from applicake.applications.commons.collector import GuseCollector, BasicCollector
from applicake.applications.commons.inifile import Unifier
from applicake.applications.commons.generator import Generator

#workflow specific inputs 
from applicake.applications.commons.generator import DatasetcodeGenerator, ParametersetGenerator

from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.openswath.splitdenoise import SplitDenoise
from applicake.applications.proteomics.openswath.rtnorm import OpenSwathRTNormalizerParallel

from applicake.applications.proteomics.openswath.analyzerparallel import OpenSwathAnalyzerParallel
 

from applicake.applications.proteomics.openswath.featurexmltotsv import FeatureXMLToTSV
from applicake.applications.proteomics.openswath.mprophet import mProphet
from applicake.applications.proteomics.openswath.featurealign import FeatureAlignment
from applicake.applications.proteomics.openbis.openswathdropbox import Copy2SwathDropbox

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
    WrapApp(SplitDenoise,input_file_name, output_file_name) 

@transform(splitwindows, regex("splitwindows.ini_*"), "irt.ini_")
def irt(input_file_name, output_file_name):
    WrapApp(OpenSwathRTNormalizerParallel, input_file_name, output_file_name) 
          
@transform(irt, regex("irt.ini_"), "openswathanalyzer.ini_")
def openswathanalyzer(input_file_name, output_file_name):  
    WrapApp(OpenSwathAnalyzerParallel, input_file_name, output_file_name) 

@transform(openswathanalyzer,regex("openswathanalyzer.ini_"), "mprophet.ini_")
def mprophet(input_file_name, output_file_name):
    WrapApp(mProphet, input_file_name, output_file_name) 

@merge(mprophet, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    argv = ['', '--COLLECTORS', 'mprophet.ini', '-o', output_file_name]
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('collector',exit_code))    

@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def paramgenerator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS','paramgenerate.ini']
    runner = IniFileRunner()
    application = ParametersetGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("paramgenerator [%s]" % exit_code)  
    
@transform(paramgenerator,regex("paramgenerate.ini_"), "featurealign.ini_")
def featurealign(input_file_name, output_file_name):
    WrapApp(FeatureAlignment, input_file_name, output_file_name) 


@transform(featurealign,regex("featurealign.ini_"), "cp2dropbox.ini_")
def copytodropbox(input_file_name, output_file_name):   
    argv = ['a','-i',input_file_name, '-o',output_file_name ]
    applic = Copy2SwathDropbox()
    runner = IniFileRunner()
    if runner(argv, applic) != 0:
        raise Exception()

########################################################

if __name__ == "__main__":
    #pipeline_printout_graph ('flowchart.png','png',[copytodropbox])
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
THREADS = 16
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

IRTTRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_DIA_iRT.TraML"

DATASET_CODE = 20120713110650516-637617, 20120713005347029-637351
TRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_AQUASky_ShotgunLibrary_3t_345_sh.TraML"

SPACE = LOBLUM
PROJECT = TEST
DROPBOX = /cluster/home/biol/loblum/swathtext/dropbox

RUNDENOISER = false,true
WIDTH = 100
RTWIDTH = 9
EXTRACTION_WINDOW = 0.05
WINDOW_UNIT = Thomson
RT_EXTRACTION_WINDOW = 300
MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95
MIN_COVERAGE = 0.6
MPR_NUM_XVAL = 5
MPR_LDA_PATH = 
MPR_MAINVAR = xx_swath_prelim_score
MPR_VARS = bseries_score elution_model_fit_score intensity_score isotope_correlation_score isotope_overlap_score library_corr library_rmsd log_sn_score massdev_score massdev_score_weighted norm_rt_score xcorr_coelution xcorr_coelution_weighted xcorr_shape xcorr_shape_weighted yseries_score
FDR = 0.01
ALIGNER_MAX_RTDIFF = 30
ALIGNER_MAX_FDRQUAL = 0.2
ALIGNER_METHOD = best_overall
""")
        sys.exit(0)
    elif sys.argv[1] == 'continue':
        print "Continuing..."
    else:
        infile = sys.argv[1]
        print "Start. Copying %s to input.ini" % infile
        shutil.copyfile(infile,'input.ini')       
    pipeline_run([copytodropbox],multiprocess=1,verbose=3)
    
