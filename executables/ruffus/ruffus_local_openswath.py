#!/usr/bin/env python
'''
Created on Jul 11, 2012

@author: quandtan, wolski, blum
'''

import os
import sys
import subprocess
import tempfile
from ruffus import *

from applicake.framework.runner import ApplicationRunnerSubfile, WrapperRunnerSubfile, IniFileRunner, IniFileRunner2, IApplication, IWrapper, WrapperRunner, CollectorRunner

from applicake.applications.commons.inifile import Unifier
from applicake.applications.commons.generator import Generator, DatasetcodeGenerator
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.openswath.splitwindows import SplitWindows
from applicake.applications.proteomics.openswath.windowgenerator import WindowGenerator
from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mzml
from applicake.applications.proteomics.openswath.irtfork import IRTFork

from applicake.applications.proteomics.openswath.chromatogramextractor import ChromatogramExtractor
from applicake.applications.commons.collector import BasicCollector, GuseCollector
from applicake.applications.proteomics.openswath.setgenerator import SetGenerator

from applicake.applications.proteomics.openswath.openswathrtnormalizer import OpenSwathRTNormalizer
from applicake.applications.proteomics.openswath.openswathanalyzer import OpenSwathAnalyzer
from applicake.applications.proteomics.openswath.featurexmltotsv import FeatureXMLToTSV
from applicake.applications.proteomics.openswath.FileMerger import ChrommzmlMerger, FeatureXMLMerger
from applicake.applications.proteomics.openswath.KeyExtract import KeyExtract
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


def WrapAppSub(applic,  input_file_name, output_file_name,opts=None):
    argv = ['fake.py', '-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    application = applic()
    if isinstance(application, IApplication):
        runner = ApplicationRunnerSubfile()
        print 'use application runner'
    elif isinstance(application, IWrapper):
        runner = WrapperRunnerSubfile()
    else:
        raise Exception('could not identfy [%s]' % applic.__name__)
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % (applic.__name__, exit_code)) 


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
IRTTRAML = "/cluster/home/biol/loblum/osw/traml/DIA_iRT.TraML"
LIBTRAML = "/cluster/home/biol/loblum/osw/traml/AQUASky_ShotgunLibrary_3t_345_sh.TraML"

#DATASET_CODE = 20120815035639258-664552, 20121025182348951-723768
#IRTTRAML = "/cluster/home/biol/loblum/osw/traml/DIA_iRT.TraML"
#LIBTRAML = "/cluster/home/biol/loblum/osw/traml/RCC_kinases.TraML"


MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95
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

@follows(splitwindows)
@split('splitwindows.ini_*', "windowgenerator.ini_*")
def WINDOWgenerator(input_file_names, notused_output_file_names):
    for idx, inputfile in enumerate(input_file_names):
        WrapApp(WindowGenerator,inputfile,'',['--GENERATORS', 'windowgenerator.ini_' + str(idx) ])  

@transform(WINDOWgenerator, regex("windowgenerator.ini_*"), 'convertmz.ini_')
def convertmz(input_file_name, output_file_name):
    WrapAppSub(Mzxml2Mzml,input_file_name, output_file_name) 

@follows(convertmz)
@split("convertmz.ini_*", "*fork.ini_*")
def IRT_fork(input_file_names, notused_output_file_name):
    for infile in input_file_names:
        outfile = 'fork.ini' + infile[infile.find('_'):]
        argv = ['fake.py', '-i', infile, '-o',outfile,'--IRTOUTPUT','IRT'+outfile]
        runner = IniFileRunner()
        application = IRTFork()
        if runner(argv, application) != 0:
            raise Exception("irtfork failed") 
    
################## iRT BRANCH #################################

@transform(IRT_fork, regex("IRTfork.ini_*"), "IRTchromatogramextractor.ini_")
def IRT_chromatogramextractor(input_file_name, output_file_name):
    WrapAppSub(ChromatogramExtractor, input_file_name, output_file_name,['-n','IRTChromatogramExtractor']) 

#this must be collate since it only merges for one Ds
@merge(IRT_chromatogramextractor,'IRTwindowcollector.ini')
def IRT_WINDOWcollector(notused_input_file_names, output_file_name):
    WrapApp(GuseCollector,'',output_file_name, ['--COLLECTORS', 'IRTchromatogramextractor.ini'])
    
@follows(IRT_WINDOWcollector)
@split("IRTwindowcollector.ini", "IRTsetgenerator.ini_*")
def IRT_SETgenerator(input_file_name,notused_file_name): 
    argv = ['fake.py', '-i', input_file_name,'--GENERATORS','IRTsetgenerator.ini','-s','memory_all']
    runner = IniFileRunner2()
    application = SetGenerator()
    if runner(argv, application) != 0:
        raise Exception("irtsetgenerator failed")
    
@transform(IRT_SETgenerator, regex("IRTsetgenerator.ini_*"),"IRTfilemerger.ini_")
def IRT_filemerger(input_file_name,output_file_name):
    WrapApp(ChrommzmlMerger, input_file_name, output_file_name)     
    
@transform(IRT_filemerger, regex("IRTfilemerger.ini_*"),"IRTopenswathrtnormalizer.ini_")
def IRT_openswathrtnormalizer(input_file_name,output_file_name):
    WrapApp(OpenSwathRTNormalizer, input_file_name,output_file_name)

################## AQUA BRANCH, REQUIRES IRT IN KEYEXTRAT#####################
  
@transform(IRT_fork, regex("^fork.ini_*"), "chromatogramextractor.ini_")
def chromatogramextractor(input_file_name, output_file_name):
    WrapAppSub(ChromatogramExtractor, input_file_name, output_file_name) 

@merge(chromatogramextractor,'IRTwindowcollector.ini')
def WINDOWcollector(notused_input_file_names, output_file_name):
    WrapApp(GuseCollector,'',output_file_name, ['--COLLECTORS', 'chromatogramextractor.ini'])
    
@follows(WINDOWcollector)
@split("windowcollector.ini", "setgenerator.ini_*")
def SETgenerator(input_file_name,notused_file_name): 
    argv = ['fake.py', '-i', input_file_name,'--GENERATORS','setgenerator.ini','-s','memory_all']
    runner = IniFileRunner2()
    application = SetGenerator()
    if runner(argv, application) != 0:
        raise Exception("setgenerator failed")
  
@collate([SETgenerator,IRT_openswathrtnormalizer], regex(r".*_(.+)$"), r'irtmerge.ini_\1')
def IRT_merge(infile, output_file_name):
     WrapApp(GuseCollector,'',output_file_name, ['--COLLECTORS', 'chromatogramextractor.ini','--COLLECTORS','IRTopenswathnormalizer.ini'])

@follows(IRT_merge)
@split("irtmerge.ini_*", "analyzergenerator.ini_*")
def ANALYZERgenerator(input_file_name,notused_file_name):
    argv = ['fake.py', '-i', input_file_name,'--GENERATORS','analyzergenerator.ini','-s','memory_all']
    runner = IniFileRunner2()
    application = AnalyzerGenerator()
    if runner(argv, application) != 0:
        raise Exception("analyzergenerator failed")
    
@transform(ANALYZERgenerator, regex("keyextract.ini_"), "openswathanalyzer.ini_")
def openswathanalyzer(input_file_name, output_file_name):  
    WrapAppSub(OpenSwathAnalyzer, input_file_name, output_file_name) 

@merge(openswathanalyzer,'analyzercollector.ini')
def ANALYZERcollector(notused_input_file_names, output_file_name):
    WrapApp(GuseCollector,'',output_file_name, ['--COLLECTORS', 'openswathanalyzer.ini'])
    
@follows(ANALYZERcollector)
@split("analyzercollector.ini", "setgenerator2.ini_*")
def SETgenerator2(input_file_name,notused_file_name): 
    argv = ['fake.py', '-i', input_file_name,'--GENERATORS','setgenerator2.ini','-s','memory_all']
    runner = IniFileRunner2()
    application = SetGenerator()
    if runner(argv, application) != 0:
        raise Exception("setgenerator failed")
        
@transform(SETgenerator2, regex("setgenerator.ini_*"),"filemerger.ini_")
def filemerger(input_file_name,output_file_name):
    WrapApp(FeatureXMLMerger, input_file_name, output_file_name) 

@transform(filemerger,regex("filemerger.ini_"), "featurexml2tsv.ini_")
def featurexmltotsv(input_file_name, output_file_name):
    WrapApp(FeatureXMLToTSV, input_file_name, output_file_name) 

#@transform(featurexmltotsv,regex("featurexml2tsv.ini_"), "mprophet.ini_")
#def mprophet(input_file_name, output_file_name):
#    WrapApp(mProphet, input_file_name, output_file_name) 

#pipeline_run([IRT_merge],multiprocess=4,verbose=2)
pipeline_printout_graph ('flowchart.png','png',[featurexmltotsv])
