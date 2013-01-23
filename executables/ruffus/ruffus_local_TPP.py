#!/usr/bin/env python
'''
Created on Aug 13, 2012

@author: quandtan
'''



import os
import sys
import subprocess

from ruffus import *
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.runner import EngineCollectorRunner
from applicake.framework.runner import IniFileRunner2, ApplicationRunner,CollectorRunner,WrapperRunner, IniFileRunner
from applicake.applications.commons.generator import DatasetcodeGenerator,\
    ParametersetGenerator
from applicake.applications.os.echo import Echo
from applicake.applications.commons.collector import GuseCollector, SimpleCollector
from applicake.applications.commons.enginecollector import GuseEngineCollector
from applicake.applications.proteomics.searchengine.xtandem import Xtandem
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.tpp.tandem2xml import Tandem2Xml
from applicake.applications.proteomics.tpp.xinteract import Xinteract
from applicake.applications.proteomics.tpp.interprophet import InterProphet
from applicake.applications.proteomics.openms.filehandling.idfileconverter import PepXml2IdXml
from applicake.applications.proteomics.openms.peptideproteinprocessing.falsediscoveryrate import FalseDiscoveryRate
from applicake.applications.proteomics.openms.peptideproteinprocessing.peptideindexer import PeptideIndexer
from applicake.applications.proteomics.openms.peptideproteinprocessing.idfilter import IdFilter
from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mzml
from applicake.applications.proteomics.openms.signalprocessing.peakpickerhighres import PeakPickerHighRes
from applicake.applications.proteomics.openms.quantification.featurefindercentroided import OrbiLessStrict
from applicake.applications.proteomics.tpp.proteinprophetFDR import ProteinProphetFDR
from applicake.applications.proteomics.sybit.protxml2spectralcount import ProtXml2SpectralCount
from applicake.applications.proteomics.sybit.protxml2modifications import ProtXml2Modifications
from applicake.applications.proteomics.sybit.protxml2openbissequence import ProtXml2OpenbisSequence
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox,\
    Copy2IdentDropbox
from applicake.applications.commons.inifile import Unifier
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.tpp.mzxml2search import Mzxml2Search
from applicake.applications.proteomics.searchengine.omssa import Omssa
from applicake.applications.proteomics.searchengine.myrimatch import Myrimatch
from applicake.applications.proteomics.searchengine.addSID2pepxml import AddSID2pepxml
from applicake.applications.proteomics.tpp.peptideprophetsequence import PeptideProphetSequence

cwd = None


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

def execute(command):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
    output, error = p.communicate()                                                                                                                                                                            
    out_stream = StringIO(output)
    err_stream = StringIO(error) 


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        subprocess.call("rm *ini* *.err *.out",shell=True)    
        with open("input.ini", 'w+') as f:
            f.write("""DATASET_CODE = 20120320163951515-361883, 20120320163653755-361882, 20120320164249179-361886
PRECMASSERR = 15
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
STORAGE = memory_all
FDR = 0.01
RUNTANDEM = True
PRECMASSUNIT = ppm
COMMENT = TPP of UPS1 ruffus
RUNMYRIMATCH = True
LOG_LEVEL = INFO
MISSEDCLEAVAGE = 1
FRAGMASSERR = 0.4
WORKFLOW = TPP_ruffus
DBASE = /cluster/scratch_xl/shareholder/imsb_ra/bin/biodb/data/ex_pd/20130117/decoy/loblum_UPS1_iRT.fasta
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/drop-box_prot_ident
DATABASE_VERSION = 20130117
XTANDEM_SCORE = k-score
SPACE = LOBLUM
DECOY_STRING = DECOY_
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows/
PROJECT = SWATH
STATIC_MODS = Carbamidomethyl (C)
DATABASE_PACKAGE = ex_pd
#-dDECOY_ DECOY=DECOY_ str used for decoys
#-OA ACCMASS accurate mass binning
#-OP NONPARAM
#-Od DECOYPROBS
#-Ol LEAVE
#-OI PI
#-Ow INSTRWARN
XINTERACT_ARGS = -dDECOY_ -OAPdlIw (dummy)
DATABASE_DB = loblum_UPS1_iRT
FRAGMASSUNIT = Da
ENZYME = Trypsin
IPROPHET_ARGS = MINPROB=0
THREADS = 4
RUNOMSSA = True""" 
#,20120603165413998-510432,
# 20120606045538225-517638 -> b10-01219.p.mzxml
# 20120603160111752-510155 -> b10-01219.c.mzxml 
# 20120124102254267-296925,20120124121656335-296961 -> orbi silac hela from petri
)       
        

@follows(setup)
@split("input.ini", "generate.ini_*")
def datasetSplit(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini','-o','generator.ini']
    runner = IniFileRunner()
    application = DatasetcodeGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
    
@transform(datasetSplit, regex("generate.ini_"), "dss.ini_")
@jobs_limit(1)
def dss(input_file_name, output_file_name):   
    wrap(Dss,input_file_name, output_file_name,['--PREFIX', 'getmsdata'])

@transform(dss, regex("dss.ini_"), "engineSplit.ini_")
def engineSplit(input_file_name, output_file_name):   
    wrap(Echo,input_file_name, output_file_name,['--PREFIX', '/bin/echo'])    
    print "NOT A CONDITIONAL WORKFLOW!!!"
       
@transform(engineSplit, regex("engineSplit.ini_"), "xtandem.ini_")
def tandem(input_file_name, output_file_name):
    wrap(Xtandem,input_file_name, output_file_name,['--PREFIX', 'tandem.exe'])

@transform(tandem, regex("xtandem.ini_"), "xtandem2xml.ini_")
def tandem2xml(input_file_name, output_file_name):
    wrap(Tandem2Xml,input_file_name, output_file_name)  

@transform(tandem2xml, regex("xtandem2xml.ini_"), "tandem.ini_")
def pepprotandem(input_file_name, output_file_name):
    wrap(PeptideProphetSequence,input_file_name, output_file_name,['-n','peptandem'])  

##################################################################################


@transform(engineSplit, regex("engineSplit.ini_"), "msconvert.ini_")
def msconvert(input_file_name, output_file_name):
    wrap(Mzxml2Search,input_file_name, output_file_name)
    
@transform(msconvert, regex("msconvert.ini_"), "omssarun.ini_")
def omssa(input_file_name, output_file_name):
    wrap(Omssa,input_file_name, output_file_name)

@transform(omssa, regex("omssarun.ini_"), "omssa.ini_")
def pepproomssa(input_file_name, output_file_name):
    wrap(PeptideProphetSequence,input_file_name, output_file_name,['-n','pepomssa','--OMSSAFIX'])       
    
###################################################################################


@transform(engineSplit, regex("engineSplit.ini_"), "myri.ini_")
def myrimatch(input_file_name, output_file_name):
    wrap(Myrimatch,input_file_name, output_file_name)

@transform(myrimatch, regex("myri.ini_"), "myriattr.ini_")
def myriaddr(input_file_name, output_file_name):
    wrap(AddSID2pepxml,input_file_name,output_file_name)
        
@transform(myriaddr, regex("myriattr.ini_"), "myrimatch.ini_")
def peppromyri(input_file_name, output_file_name):
    wrap(PeptideProphetSequence,input_file_name, output_file_name,['-n','pepmyri'])       
    

############################# MERGE SEARCH ENGINE RESULTS ################################## 
#.*_(.+)$ = any char any no. times, underscore, "group" with at least one char, end of line  
#"groups" are acessible with \n afterwards (.* is not a group!)
@merge([pepproomssa,pepprotandem,peppromyri], 'output.ini')
def mergeEngines(input_file_names, output_file_name):
    argv = ['','-i','generator.ini','--ENGINES','tandem','--ENGINES','myrimatch','--ENGINES','omssa','-o','output.ini']
    runner = IniFileRunner()
    application = GuseEngineCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("engine failed [%s]" % exit_code) 
 

@follows(mergeEngines)
@split("output.ini", "output.ini_*")
def fakesplit(inn,outt):
    pass
    
@transform(fakesplit, regex("output.ini_"), "interprophetengines.ini_")
def interprophetengines(input_file_name, output_file_name):
    wrap(InterProphet,input_file_name, output_file_name)
       
    
############################# TAIL: PARAMGENERATE ##################################   

@merge(interprophetengines, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    argv = ['', '--COLLECTORS', 'interprophetengines.ini', '-o', output_file_name]
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('collector',exit_code))    

@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def parameterSplit(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS','paramgenerate.ini','-o','paramgenerator.ini']
    runner = IniFileRunner2()
    application = ParametersetGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("paramgenerator [%s]" % exit_code)  

@transform(parameterSplit, regex("paramgenerate.ini_"), "interprophetparam.ini_")
def interprophetParam(input_file_name, output_file_name):
    wrap(InterProphet,input_file_name, output_file_name,['-n','iproparam'])  

@transform(interprophetParam, regex("interprophetparam.ini_"), "proteinprophet.ini_") 
def proteinprophet(input_file_name, output_file_name):
    wrap(ProteinProphetFDR,input_file_name, output_file_name)

@transform(proteinprophet, regex("proteinprophet.ini_"), "protxml2openbis.ini_")
def protxml2openbis(input_file_name, output_file_name):
    wrap(ProtXml2OpenbisSequence,input_file_name, output_file_name)

@transform(protxml2openbis, regex("protxml2openbis.ini_"),"copy2dropbox.ini_")
def copy2dropbox(input_file_name, output_file_name):
    argv = ["", "-i", input_file_name, "-o",output_file_name,"-p"]
    runner = IniFileRunner()
    application = Copy2IdentDropbox()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("copy2dropbox [%s]" % exit_code)  


pipeline_run([copy2dropbox], multiprocess = 9)

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
