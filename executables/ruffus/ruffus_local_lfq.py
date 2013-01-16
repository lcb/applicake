#!/usr/bin/env python
'''
Created on Aug 15, 2012

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

from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mzml
from applicake.applications.proteomics.openms.signalprocessing.peakpickerhighres import PeakPickerHighRes
from applicake.applications.proteomics.openms.quantification.featurefindercentroided import FeatureFinderCentroided
from applicake.applications.proteomics.openms.filehandling.idfileconverter import ProtXml2IdXml
from applicake.applications.proteomics.openms.peptideproteinprocessing.idfilter import IdFilter
from applicake.applications.proteomics.openswath import KeyExtract
from applicake.applications.proteomics.openms.peptideproteinprocessing.idmapper import IdMapper
from applicake.applications.proteomics.openms.mapalignment.mappaligneridentification import MapAlignerIdentification
from applicake.applications.proteomics.openms.quantification.proteinquantifier import ProteinQuantifier
from applicake.applications.proteomics.sybit.annotxmlfromcsv import AnnotProtxmlFromCsv
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

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
LOG_LEVEL = INFO
STORAGE = memory_all
WORKFLOW = ruffus_LFQ

EXPERIMENT = E286955
FDR = 0.01
THREADS = 4
""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    
@follows(setup)
def getexperiment():
     wrap(Dss,'input.ini','getexperiment.ini',['--PREFIX', 'getexperiment'])

@follows(getexperiment)
def processexperiment():
    wrap(ProcessExperiment,'getexperiment.ini','processexperiment.ini',['--GETCODES','True'])
    
################################## ID Extraction ############################################

@follows(processexperiment)   
def idfileconverter():
    wrap(ProtXml2IdXml,'processexperiment.ini','idfileconverter.ini')
    
@follows(idfileconverter)
def idfilter():
    wrap(IdFilter,'idfileconverter.ini','idfilter.ini')
    

################################## Picking ##################################################

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
    
@transform(dss, regex("dss.ini_"), "fileconverter.ini_")
def fileconverter(input_file_name, output_file_name):
    wrap(Mzxml2Mzml,input_file_name,output_file_name)
    
@transform(fileconverter, regex("fileconverter.ini_"), "peakpicker.ini_")
def peakpicker(input_file_name, output_file_name):
    wrap(PeakPickerHighRes,input_file_name,output_file_name)    

@transform(peakpicker, regex("peakpicker.ini_"), "featurefinder.ini_")
def featurefinder(input_file_name, output_file_name):
    wrap(FeatureFinderCentroided,input_file_name,output_file_name)

################################# Merge ID Extract and Picking ##############################

@transform([featurefinder,idfilter], regex("featurefinder.ini_"), "keyextract.ini_")
def keyextract(input_file_name, output_file_name):
    wrap(KeyExtract, input_file_name, output_file_name, ['--KEYFILE','idfilter.ini','--KEYSTOEXTRACT','IDXML']) 

@transform(keyextract, regex("keyextract.ini_"), "idmapper.ini_")
def idmapper(input_file_name, output_file_name):
    wrap(IDMapper, input_file_name, output_file_name) 
    
@transform(idmapper, regex("idmapper.ini_"), "mapaligner.ini_")
def mapaligner(input_file_name, output_file_name):
    wrap(MapAligner, input_file_name, output_file_name) 
    
@transform(mapaligner, regex("mapaligner.ini_"), "featurelinker.ini_")
def featurelinker(input_file_name, output_file_name):
    wrap(FeatureLinker, input_file_name, output_file_name) 


@merge(featurelinker, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    argv = ['', '--COLLECTORS', 'featurelinker.ini', '-o', output_file_name,'-s','file']
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('collector',exit_code))    

@follows(collector)
def unifier():
    argv = ['', '-i', 'collector.ini', '-o','unifier.ini','--UNIFIER_REDUCE','--LISTS_TO_REMOVE','PARAM_IDX','--LISTS_TO_REMOVE','FILE_IDX']
    runner = IniFileRunner2()
    application = Unifier()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("unifier [%s]" % exit_code)
        
@follows(unifier)
def proteinquantifier():
    wrap(ProteinQuantifier,'unifier.ini','proteinquantifier.ini')
    
@follows(proteinquantifier)
def annotxml():
    wrap(AnnotProtxmlFromCsv,'proteinquantifier.ini','annotxml.ini')
    
@follows(annotxml)
def cp2dropbox():
    wrap(Copy2Dropbox,'annotxml.ini','cp2dropbox.ini')

pipeline_run([cp2dropbox], multiprocess=16)
#pipeline_printout_graph ('flowchart.png','png',[idfilter],no_key_legend = False) #svg
