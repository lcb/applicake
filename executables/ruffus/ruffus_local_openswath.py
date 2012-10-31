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

from applicake.utils.ruffusutils import WrapApp

from applicake.framework.interfaces import IApplication, IWrapper
from applicake.framework.runner import ApplicationRunner, CollectorRunner, WrapperRunner, IniFileRunner, IniFileRunner2
from applicake.applications.commons.generator import Generator
from applicake.applications.commons.collector import BasicCollector

from applicake.applications.commons.generator import DatasetcodeGenerator
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.openswath.splitgenerator import SplitGenerator, IRTGenerator
from applicake.applications.proteomics.openswath.splitwindows import SplitWindows

from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mzml
from applicake.applications.proteomics.openswath.chromatogramextractor import ChromatogramExtractor
from applicake.applications.proteomics.openswath.mrmrtnormalizer import MRMRTNormalizer
from applicake.applications.proteomics.openswath.mrmanalyzer import MRMAnalyzer
from applicake.applications.proteomics.openswath.featurexmltotsv import FeatureXMLToTSV
from applicake.applications.proteomics.openswath.FileMerger import FileMerger
from applicake.applications.proteomics.openswath.KeyExtract import KeyExtract
from applicake.applications.commons.collector import GuseCollector
from applicake.applications.commons.inifile import Unifier
from applicake.framework.enums import KeyEnum

def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        subprocess.call("rm *ini* *.err *.out",shell=True)    
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
LOG_LEVEL = INFO
STORAGE = memory_all
THREADS = 2
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

DATASET_CODE = 20121002200049906-707790, 20121019204406445-717969
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
@split("input.ini", "generatedss.ini_*")
def DSSgenerator(input_file_name, notused_output_file_names):
    WrapApp(DatasetcodeGenerator, input_file_name, '', ['--GENERATORS', 'generatedss.ini'])

@transform(DSSgenerator, regex("generatedss.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata',dir='.')   
    WrapApp(Dss,input_file_name, output_file_name,['--PREFIX', 'getmsdata','--RESULT_FILE',tfile])


@transform(dss, regex("dss.ini_"), "splitwindows.ini_")
def splitwindows(input_file_name, output_file_name):
    WrapApp(SplitWindows,input_file_name, output_file_name) 

@follows(splitwindows)
@split('splitwindows.ini_*', "generatewindows.ini*")
def Windowgenerator(input_file_names, notused_output_file_names):
    for inputfile in input_file_names:
        num = inputfile.split("_")[1]
        WrapApp(SplitGenerator,inputfile,'',['--GENERATORS', 'generatewindows.ini_' + num])  

@transform(Windowgenerator, regex("generatewindows.ini_"), "convertmz.ini_")
def convertmz(input_file_name, output_file_name):
    WrapApp(Mzxml2Mzml,input_file_name, output_file_name) 

#I hope this can be done more easily in gUSE
@follows(convertmz)
@split('convertmz.ini_*', "*splitce.ini_*")
def IRTsplitter(input_file_names, notused_output_file_names):
    for inputfile in input_file_names:
        outfile = 'splitce.ini' + inputfile[inputfile.find('_'):]
        WrapApp(IRTGenerator,inputfile,'',['--GENERATORS', outfile])
        
################## iRT BRANCH #################################

@transform(IRTsplitter, regex("IRTsplitce.ini_"), "IRTchromatogramextractor.ini_")
def IRTchromatogramExtractor(input_file_name, output_file_name):
    WrapApp(ChromatogramExtractor, input_file_name, output_file_name,['-n','IRTChromatogramExtractor']) 

@merge(IRTchromatogramExtractor,'IRTwindowcollector.ini')
def IRTWindowcollector(notused_input_file_names, output_file_name):
    WrapApp(CollectorRunner,'',output_file_name, ['--COLLECTORS', 'IRTchromatogramextractor.ini','-s','memory_all'])
    
@follows(IRTWindowcollector)
def IRTunifier():
    WrapApp(Unifier,'IRTwindowcollector.ini','IRTunifier.ini',['--UNIFIER_REDUCE','-s','file'])
    
@follows(IRTunifier)
def IRTfilemerger():
    WrapApp(FileMerger, 'IRTunifier.ini', 'IRTfilemerger.ini',['-s','file'])     
    
@follows(IRTfilemerger)
def IRTmrmrtnormalizer():
    WrapApp(MRMRTNormalizer, 'IRTfilemerger.ini', 'IRTmrmrtnormalizer.ini')

################## AQUA BRANCH, REQUIRES IRT IN KEYEXTRAT#####################
  
@transform(IRTsplitter, regex("splitce.ini_"), "chromatogramextractor.ini_")
def chromatogramExtractor(input_file_name, output_file_name):
    WrapApp(ChromatogramExtractor, input_file_name, output_file_name) 

@transform([chromatogramExtractor,IRTmrmrtnormalizer], regex("chromatogramextractor.ini_"), "keyextract.ini_")
def keyextract(input_file_name, output_file_name):
    WrapApp(KeyExtract, input_file_name, output_file_name, ['--KEYFILE','IRTmrmrtnormalizer.ini','--KEYSTOEXTRACT','TRAFOXML']) 

@transform([keyextract,], regex("keyextract.ini_"), "mrmanalyzer.ini_")
def mrmanalyzer(input_file_name, output_file_name):  
    WrapApp(MRMAnalyzer, input_file_name, output_file_name) 

@transform(mrmanalyzer,regex("mrmanalyzer.ini_"), "featurexml2tsv.ini_")
def featurexmltotsv(input_file_name, output_file_name):
    WrapApp(FeatureXMLToTSV, input_file_name, output_file_name) 

@collate(mrmanalyzer,regex(r".*_(.+)_.*$"),  r'windowcollector.ini_\1')
def Windowcollector(input_file_names, output_file_name):
    for f in input_file_names:
        WrapApp(CollectorRunner,'',output_file_name, ['--COLLECTORS', 'featurexml2tsv.ini','-s','memory_all'])


@merge(Windowcollector,'windowcollector.ini')
def DSScollector(notused_input_file_names, output_file_name):
    WrapApp(CollectorRunner,'',output_file_name, ['--COLLECTORS', 'windowcollector.ini','-s','memory_all'])

     
       
pipeline_run([IRTmrmrtnormalizer],multiprocess=4,verbose=2)
#pipeline_printout_graph ('flowchart.png','png',[DSScollector])