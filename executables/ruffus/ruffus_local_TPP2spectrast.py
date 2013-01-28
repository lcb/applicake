#!/usr/bin/env python
'''
Created on Oct 18, 2012

@author: quandtan, loblum
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
from applicake.applications.commons.inifile import KeysToList, Unifier
from applicake.applications.proteomics.spectrast.libcreator import RawLibraryNodecoy ,\
    RTLibrary, CreateTxtLibrary
from applicake.applications.commons.collector import GuseCollector,\
    SimpleCollector
from applicake.applications.proteomics.srm.sptxt2csv import Sptxt2Csv
from applicake.applications.proteomics.srm.converttsv2traml import ConvertTSVToTraML
from applicake.framework import enums
from applicake.framework.enums import KeyEnum
from applicake.framework.informationhandler import BasicInformationHandler
from applicake.applications.proteomics.spectrast.spectrastirtcalibrator import SpectrastIrtCalibrator 
from applicake.applications.proteomics.openswath.decoygen import OpenSwathDecoyGenerator
from applicake.applications.proteomics.spectrast.spectrast2traml import Spectrast2TraML
    
#helper function
def wrap(applic,  input_file_name, output_file_name,opts=None):
    argv = ['', '-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    application = applic()
    if isinstance(application, IApplication):
        runner = ApplicationRunner()
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
LOG_LEVEL = INFO
STORAGE = memory_all
WORKFLOW = traml_create
EXPERIMENT = E287728
THREADS = 8

#fdr2prob
DECOY_STRING = DECOY_
FDR=0.01
PROPHET_TYPE = IProphet
FDR_LEVEL = psm
NUM_LIMIT = 0
MIN_PROB = 0.0001

#sptxt2csv
LOW_MZ_CUTOFF=300
MIN_NR_TR=2
MAX_NR_TR=6

#spectrast2spectrast_irt
RSQ_THRESHOLD = 0.5

#decoygen
SWDECOY_METHOD = shuffle
SWDECOY_THEORETICAL = False

#cp2traml
TRAML_DIR = /cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile
TRAML_NAME = loblum_PA1.traml
""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    
@follows(setup)
@files('input.ini','getexperiment.ini')
def getexperiment(input_file_name,output_file_name):
     wrap(Dss,input_file_name,output_file_name,['--PREFIX', 'getexperiment'])

@follows(getexperiment)
@files('getexperiment.ini','processexperiment.ini')
def processexperiment(input_file_name,output_file_name):
    wrap(ProcessExperiment,input_file_name,output_file_name,['--GETCODES','True'])

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
    argv = ['', '--COLLECTORS', 'dss.ini', '-o', output_file_name,]
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('collector',exit_code))    

#@follows(collector)
#@split("collector.ini", "paramgenerate.ini_*")
#    argv = ['', '-i', input_file_name, '--GENERATORS','paramgenerate.ini','-o','paramgenerator.ini']
##def paramgenerator(input_file_name, notused_output_file_names):
#    runner = IniFileRunner2()
#    application = ParametersetGenerator()
#    exit_code = runner(argv, application)
#    if exit_code != 0:
#        raise Exception("paramgenerator [%s]" % exit_code)  
  
@transform(paramgenerator,regex('paramgenerate.ini_'),'rawlibnodecoy.ini_')
def rawlibnodecoy(input_file_name, output_file_name):
    wrap(RawLibraryNodecoy,input_file_name, output_file_name)

#########OPTIONAL################
  
@transform(rawlibnodecoy,regex('rawlibnodecoy.ini_'),'txtlib.ini_')
def txtlib(input_file_name, output_file_name):
    wrap(CreateTxtLibrary,input_file_name, output_file_name)         

@transform(txtlib,regex('txtlib.ini_'),'irtcalibration.ini_')
def irtcalibration(input_file_name, output_file_name):
    wrap(SpectrastIrtCalibrator,input_file_name, output_file_name)

@transform(irtcalibration,regex('irtcalibration.ini_'),'binlib.ini_')
def binlib(input_file_name, output_file_name):
    wrap(RTLibrary,input_file_name, output_file_name)

    
##############################SECOND PART
#conditiona
@transform(irtcalibration,regex('irtcalibration.ini_'),'trameler.ini_')
def trameler(input_file_name, output_file_name):
    wrap(Spectrast2TraML,input_file_name, output_file_name) 

pipeline_run([trameler], verbose=2, multiprocess=8)
