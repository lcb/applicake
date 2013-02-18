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
from applicake.applications.proteomics.sybit.keyextract import KeyExtract
from applicake.applications.proteomics.openms.peptideproteinprocessing.idmapper import IdMapper
from applicake.applications.proteomics.openms.mapalignment.mappaligneridentification import MapAlignerIdentification
from applicake.applications.proteomics.openms.quantification.proteinquantifier import ProteinQuantifier
from applicake.applications.proteomics.sybit.annotxmlfromcsv import AnnotProtxmlFromCsv
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox
from applicake.applications.proteomics.openms.quantification.lfqpart1 import LFQpart1
from applicake.applications.proteomics.openms.quantification.lfqpart2 import LFQpart2
from applicake.applications.proteomics.openms.filehandling.idfileconverter import PepXml2IdXml
from applicake.applications.commons.collector import GuseCollector
from applicake.applications.commons.inifile import Unifier
from applicake.applications.proteomics.openms.quantification.rewriteprotxml import RewriteAbundancesToProtXML
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
DATASET_CODE =  20121111164535033-734577, 20121111202839878-734779, 20121111030327351-734253, 20121111061258331-734296, 20121112035136561-734911, 20121110192440296-733977, 20121111130631004-734532, 20121111093340399-734380, 20121110224801061-734044, 20121111235146323-734856

PEPXML_FDR = 0.01

FEATUREFINDER_MASS_TRACE__MZ_TOLERANCE = 0.03
FEATUREFINDER_MASS_TRACE__MIN_SPECTRA = 5
FEATUREFINDER_MASS_TRACE__MAX_MISSING = 2
FEATUREFINDER_MASS_TRACE__SLOPE_BOUND = 1
FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_LOW = 2
FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_HIGH = 6
FEATUREFINDER_ISOTOPIC_PATTERN__MZ_TOLERANCE = 0.03
FEATUREFINDER_SEED__MIN_SCORE = 0.1
FEATUREFINDER_FEATURE__MIN_SCORE = 0.3
FEATUREFINDER_FEATURE__MIN_ISOTOPE_FIT = 0.1
FEATUREFINDER_FEATURE__MIN_TRACE_SCORE = 0.1
FEATUREFINDER_USER_SEED__MIN_SCORE = 0.1
FEATUREFINDER_USER_SEED__RT_TOLERANCE = 120
FEATUREFINDER_USER_SEED__MZ_TOLERANCE = 0.1
FEATURELINKER_USE_IDENTIFICATIONS = true
FEATURELINKER_DISTANCE_RT__MAX_DIFFERENCE = 120
FEATURELINKER_DISTANCE_MZ__MAX_DIFFERENCE = 0.02
FEATURELINKER_DISTANCE_MZ__UNIT = DA
IDMAPPER_MZ_TOLERANCE = 40
IDMAPPER_MZ_REFERENCE = peptide
IDMAPPER_USE_CENTROID_MZ = true
IDMAPPER_RT_TOLERANCE= 10
MAPALIGNER_MODEL__TYPE = b_spline
MAPALIGNER_ALGORITHM__MAX_RT_SHIFT = 0.2
PEAKPICKER_SIGNAL_TO_NOISE = 0
PEAKPICKER_MS1_ONLY = true
PROTEINQUANTIFIER_INCLUDE_ALL = true
PROTEINQUANTIFIER_TOP = 1
SEEDLISTGENERATOR_USE_PEPTIDE_MASS = true


EXPERIMENT = E286955
FDR = 0.01
THREADS = 4
""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    
@follows(setup)
@files('input.ini','getexperiment.ini')
def getexperiment(input,output):
     wrap(Dss,input,output,['--PREFIX', 'getexperiment'])

@follows(getexperiment)
@files('getexperiment.ini','processexperiment.ini')
def processexperiment(input,output):
    wrap(ProcessExperiment,input,output)

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

################################################################################################


@transform(dss, regex("dss.ini_"), "lfqpart1.ini_")
def lfqpart1(input_file_name, output_file_name):
    wrap(LFQpart1,input_file_name,output_file_name)


@merge(lfqpart1, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    argv = ['', '--COLLECTORS', 'lfqpart1.ini', '-o', output_file_name]
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("collector failed [%s]" % exit_code)    

@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def paramgenerator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS','paramgenerate.ini','-o','paramgenerator.ini','-s','memory_all']
    runner = IniFileRunner2()
    application = ParametersetGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("paramgenerator [%s]" % exit_code)
 
        
@follows(paramgenerator)
@transform(paramgenerator,regex("paramgenerate.ini_"),"lfqpart2.ini_")
def lfqpart2(input_file_name, output_file_name):
    wrap(LFQpart2,input_file_name,output_file_name)        

@transform(lfqpart2,regex("lfqpart2.ini_"),"rewritexml.ini_")
def rewritexml(input_file_name, output_file_name):
    wrap(RewriteAbundancesToProtXML,input_file_name,output_file_name)      
    
pipeline_run([rewritexml], multiprocess=16)
#pipeline_printout_graph ('flowchart.png','png',[idfilter],no_key_legend = False) #svg