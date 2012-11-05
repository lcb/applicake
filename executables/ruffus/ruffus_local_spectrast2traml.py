#!/usr/bin/env python
'''
Created on Oct 18, 2012

@author: quandtan
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
from applicake.applications.proteomics.sybit.pepxml2csv import Pepxml2Csv
from applicake.applications.proteomics.sybit.fdr2probability import Fdr2Probability,\
    Fdr2ProbabilityPython
from applicake.applications.commons.inifile import KeysToList, Unifier
from applicake.applications.proteomics.spectrast.libcreator import RawLibrary ,\
    NoDecoyLibrary, ConsensusLibrary, CreateTxtLibrary, CreateBinLibrary
from applicake.applications.commons.collector import GuseCollector,\
    SimpleCollector
from applicake.applications.proteomics.srm.sptxt2csv import Sptxt2Csv
from applicake.applications.proteomics.srm.converttsv2traml import ConvertTSVToTraML
from applicake.framework import enums
from applicake.framework.enums import KeyEnum
from applicake.framework.informationhandler import BasicInformationHandler
from applicake.applications.proteomics.spectrast.spectrastirtcalibrator import SpectrastIrtCalibrator
    
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
STORAGE = file
WORKFLOW = spectrast_create
EXPERIMENT = E286955
DATASET_CODE = 20110721034730308-201103,20110721054532782-201128,20110721073234274-201170,20110721173145616-201355,20110721210947748-201441,20110721233250123-201503,20110722014852343-201543,20110722033454238-201588
FDR=0.01
FDR_LEVEL = psm
NUM_LIMIT = 0
MIN_PROB = 0.0001
PROPHET_TYPE = IProphet
DECOY_STRING = DECOY_
RSQ_THRESHOLD = 0.95
""")
            #E286966
            #20120928124818478-704737,
            # EXPERIMENT = E286955
            #DATASET_CODE = 20110722014852343-201543, 20110722033454238-201588
            
            
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    
@follows(setup)
def getexperiment():
     wrap(Dss,'input.ini','getexperiment.ini',['--PREFIX', 'getexperiment'])

@follows(getexperiment)
def processexperiment():
    wrap(ProcessExperiment,'getexperiment.ini','processexperiment.ini')

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

@merge(dss, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    argv = ['', '--COLLECTORS', 'dss.ini', '-o', output_file_name,'-s','file']
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('collector',exit_code))    

@follows(collector)
def unifier():
    argv = ['','-i', 'collector.ini', '-o','unifier.ini','--UNIFIER_REDUCE']
    runner = IniFileRunner2()
    application = Unifier()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('unifier',exit_code))  

@follows(unifier)
@split("unifier.ini", "paramgenerate.ini_*")
def paramgenerator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS','paramgenerate.ini','-o','paramgenerator.ini']
    runner = IniFileRunner2()
    application = ParametersetGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("paramgenerator [%s]" % exit_code)  
    
    
@transform(paramgenerator, regex("paramgenerate.ini_"), "pepxmlskey2list.ini_")
def pepxmlskey2list(input_file_name, output_file_name):
    argv = ['', '-i', input_file_name, '-o',output_file_name,'--KEYSTOLIST','PEPXMLS']
    runner = IniFileRunner()
    application = KeysToList()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("paramgenerator [%s]" % exit_code)      

@transform(pepxmlskey2list, regex("pepxmlskey2list.ini_"), "pepxml2csv.ini_")
def pepxml2csv(input_file_name, output_file_name):
    wrap(Pepxml2Csv,input_file_name, output_file_name)          
    
@transform(pepxml2csv, regex("pepxml2csv.ini_"), "fdr2probability.ini_")
def fdr2probability(input_file_name, output_file_name):
    #wrap(Fdr2Probability,input_file_name, output_file_name)
    wrap(Fdr2ProbabilityPython,input_file_name, output_file_name) 
    
@transform(fdr2probability,regex('fdr2probability.ini_'),'rawlibcreator.ini_')
def rawlib(input_file_name, output_file_name):
    wrap(RawLibrary,input_file_name, output_file_name)
    
@transform(rawlib,regex('rawlibcreator.ini_'),'nodecoylib.ini_')
def nodecoylib(input_file_name, output_file_name):
    wrap(NoDecoyLibrary,input_file_name, output_file_name)         

#@transform(nodecoylib,regex('nodecoylib.ini_'),'irtcalibration.ini_')
#def irtcalibration(input_file_name, output_file_name):
#    wrap(SpectrastIrtCalibrator,input_file_name, output_file_name,['--PREFIX','/cluster/apps/openms/openswath-testing/mapdiv/scripts/assays/spectrast2spectrast_irt.py',
#                                                                   '-s','memory_all'])

#@transform(irtcalibration,regex('irtcalibration.ini_'),'consensuslib.ini_')
@transform(nodecoylib,regex('nodecoylib.ini_'),'consensuslib.ini_')
def consensuslib(input_file_name, output_file_name):
    wrap(ConsensusLibrary,input_file_name, output_file_name) 

#@transform(consensuslib,regex('consensuslib.ini_'),'createtxtlib.ini_')
#def createtxtlib(input_file_name, output_file_name):
#    wrap(CreateTxtLibrary,input_file_name, output_file_name)

#@transform(createtxtlib,regex('createtxtlib.ini_'),'sptxt2tracsv.ini_')
@transform(consensuslib,regex('consensuslib.ini_'),'sptxt2tracsv.ini_')
def sptxt2tracsv(input_file_name, output_file_name):
    wrap(Sptxt2Csv,input_file_name, output_file_name,['--PREFIX','/cluster/apps/openms/openswath-testing/mapdiv/scripts/assays/sptxt2csv.py']) 

@transform(sptxt2tracsv,regex('sptxt2tracsv.ini_'),'tracsv2traml.ini_')
def tracsv2traml(input_file_name, output_file_name):
    wrap(ConvertTSVToTraML,input_file_name, output_file_name,['--%s' % KeyEnum.THREADS,'1',
                                                              '--%s' % KeyEnum.PREFIX,'module unload openms;module unload openms;module load openms/svn;ConvertTSVToTraML']) 

#@transform(tracsv2traml,regex('tracsv2traml.ini_'),'createbinlib.ini_')
#def createbinlib(input_file_name, output_file_name):
#    wrap(CreateBinLibrary,input_file_name, output_file_name)


pipeline_run([tracsv2traml], multiprocess=3)