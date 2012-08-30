#!/usr/bin/env python
'''
Created on Aug 31, 2012

@author: quandtan
'''

import os
import sys
import subprocess

from ruffus import *
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.runner import IniFileRunner2, ApplicationRunner,CollectorRunner,WrapperRunner, IniFileRunner
from applicake.applications.commons.generator import DatasetcodeGenerator,\
    ParametersetGenerator
from applicake.applications.os.echo import Echo
from applicake.applications.commons.collector import GuseCollector, SimpleCollector
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
from applicake.applications.proteomics.sybit.pepxml2csv import Pepxml2Csv
from applicake.applications.proteomics.sybit.fdr2probability import Fdr2Probability
from applicake.applications.proteomics.tpp.proteinprophet import ProteinProphet
from applicake.applications.proteomics.sybit.protxml2spectralcount import ProtXml2SpectralCount
from applicake.applications.proteomics.sybit.protxml2modifications import ProtXml2Modifications
from applicake.applications.proteomics.sybit.protxml2openbis import ProtXml2Openbis
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox,\
    Copy2IdentDropbox
from applicake.applications.commons.inifile import Unifier
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.proteowizard.msconvert import Mzxml2Mgf
from applicake.applications.proteomics.searchengine.omssa import Omssa
from applicake.applications.proteomics.searchengine.myrimatch import Myrimatch

from applicake.applications.proteomics.tpp.interactparser import InteractParser
from applicake.applications.proteomics.tpp.refreshparser import RefreshParser
from applicake.applications.proteomics.tpp.peptideprophet import PeptideProphet

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

def setup():
    subprocess.call("rm *ini*",shell=True)    
    with open("input.ini", 'w+') as f:
        f.write("""BASEDIR = /cluster/scratch/malars/workflows
LOG_LEVEL = DEBUG
STORAGE = file

DATASET_DIR = /cluster/scratch/malars/datasets
DATASET_CODE = 20111212003510002-282406,20111212212548508-282587
DBASE = /cluster/scratch/malars/biodb/ex_sp/current/decoy/ex_sp_9606.fasta

DECOY_STRING = DECOY_ 
FRAGMASSERR = 0.4
FRAGMASSUNIT = Da
PRECMASSERR = 15,25
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
ENZYME = Trypsin
STATIC_MODS = Carbamidomethyl (C),13C(6)15(N)(2) (K),13C(6)15(N)(4) (R)
VARIABLE_MODS =
THREADS = 4
XTANDEM_SCORE = k-score
IPROPHET_ARGS = MINPROB=0
FDR=0.01
SPACE = QUANDTAN
PROJECT = TEST
DROPBOX = /cluster/scratch/malars/drop-box_prot_ident
WORKFLOW= ruffus_drmaa_ommyxt
COMMENT = yancheng silac test
""" 
#,20120603165413998-510432,
# 20120606045538225-517638 -> b10-01219.p.mzxml
# 20120603160111752-510155 -> b10-01219.c.mzxml 
# 20120124102254267-296925,20120124121656335-296961 -> orbi silac hela from petri
)       
        

@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini','-o','generator.ini']
    runner = IniFileRunner()
    application = DatasetcodeGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
    
@transform(generator, regex("generate.ini_"), "dss.ini_")
@jobs_limit(1)
def dss(input_file_name, output_file_name):   
    wrap(Dss,input_file_name, output_file_name,['--PREFIX', 'getmsdata'])


######################### TANDEM #########################################
        
@transform(dss, regex("dss.ini_"), "xtandem.ini_")
def tandem(input_file_name, output_file_name):
    wrap(Xtandem,input_file_name, output_file_name,['--PREFIX', 'tandem.exe'])

@transform(tandem, regex("xtandem.ini_"), "xtandem2xml.ini_")
def tandem2xml(input_file_name, output_file_name):
    wrap(Tandem2Xml,input_file_name, output_file_name)  

@transform(tandem2xml, regex("xtandem2xml.ini_"), "tandeminteract.ini_")
def tandeminteract(input_file_name, output_file_name,):
    wrap(InteractParser,input_file_name, output_file_name,['-n','tandeminteract'])   

@transform(tandeminteract, regex("tandeminteract.ini_"), "tandemrefresh.ini_")
def tandemrefresh(input_file_name, output_file_name):
    wrap(RefreshParser,input_file_name, output_file_name,['-n','tandemrefresh']) 

@transform(tandemrefresh, regex("tandemrefresh.ini_"), "tandempeppro.ini_")
def tandemPepPro(input_file_name, output_file_name):
    wrap(PeptideProphet,input_file_name, output_file_name,['-n','tandemppeppro']) 

########################### OMSSA #######################################


@transform(dss, regex("dss.ini_"), "myrimatch.ini_")
def myrimatch(input_file_name, output_file_name):
    wrap(Myrimatch,input_file_name, output_file_name)

@transform(myrimatch, regex("myrimatch.ini_"), "myrirefresh.ini_")
def myrirefresh(input_file_name, output_file_name):
    wrap(RefreshParser,input_file_name, output_file_name,['-n','myrirefresh']) 

@transform(myrirefresh, regex("myrirefresh.ini_"), "myriinteract.ini_")
def myriinteract(input_file_name, output_file_name,):
    wrap(InteractParser,input_file_name, output_file_name,['-n','myriinteract'])   

@transform(myriinteract, regex("myriinteract.ini_"), "myrirefresh2.ini_")
def myrirefresh2(input_file_name, output_file_name):
    wrap(RefreshParser,input_file_name, output_file_name,['-n','myrirefresh2']) 

@transform(myrirefresh2, regex("myrirefresh2.ini_"), "myripeppro.ini_")
def myriPepPro(input_file_name, output_file_name):
    wrap(PeptideProphet,input_file_name, output_file_name,['-n','myrippeppro']) 
    
########################### MYRIMATCH ########################################

@transform(dss, regex("dss.ini_"), "msconvert.ini_")
def msconvert(input_file_name, output_file_name):
    wrap(Mzxml2Mgf,input_file_name, output_file_name,['-s','file','-l','DEBUG'])
    
@transform(msconvert, regex("msconvert.ini_"), "omssa.ini_")
def omssa(input_file_name, output_file_name):
    wrap(Omssa,input_file_name, output_file_name)

@transform(omssa, regex("omssa.ini_"), "omssainteract.ini_")
def omssainteract(input_file_name, output_file_name):
    wrap(InteractParser,input_file_name, output_file_name,['-n','omssainteract'])   

@transform(omssainteract, regex("omssainteract.ini_"), "omssarefresh.ini_")
def omssarefresh(input_file_name, output_file_name):
    wrap(RefreshParser,input_file_name, output_file_name,['-n','omssarefresh']) 

@transform(omssarefresh, regex("omssarefresh.ini_"), "omssapeppro.ini_")
def omssaPepPro(input_file_name, output_file_name):
    wrap(PeptideProphet,input_file_name, output_file_name,['-n','omssappeppro'])  
 
############################# MERGE SEARCH ENGINE RESULTS ################################## 
#.*_(.+)$ = any char any no. times, underscore, "group" with at least one char, end of line  
#"groups" are acessible with \n afterwards (.* is not a group!)
@collate([omssaPepPro,tandemPepPro,myriPepPro],regex(r".*_(.+)$"),  r'mergeengines.ini_\1')
def mergeEngines(input_file_names, output_file_name):
    argv = ['']
    for f in input_file_names:
        argv.append('--COLLECTORS')
        argv.append(f)
    argv.append('-o')
    argv.append(output_file_name)
    
    runner = CollectorRunner()
    application = SimpleCollector()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("collector failed [%s]" % exit_code) 

@transform(mergeEngines, regex("mergeengines.ini_"), "unifyengines.ini_")
def unifyEngines(input_file_name, output_file_name):
    argv = ['', '-i', input_file_name, '-o',output_file_name,'--UNIFIER_REDUCE']
    runner = IniFileRunner2()
    application = Unifier()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("unifier failed [%s]" % exit_code)  

@transform(unifyEngines, regex("unifyengines.ini_"), "interprophetengines.ini_")
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
def paramgenerator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS','paramgenerate.ini','-o','paramgenerator.ini','-s','file']
    runner = IniFileRunner()
    application = ParametersetGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("paramgenerator [%s]" % exit_code)  

@transform(paramgenerator, regex("paramgenerate.ini_"), "interprophet.ini_")
def interprophet(input_file_name, output_file_name):
    wrap(InterProphet,input_file_name, output_file_name)

@transform(interprophet, regex("interprophet.ini_"), "pepxml2csv.ini_")
def pepxml2csv(input_file_name, output_file_name):
    wrap(Pepxml2Csv,input_file_name, output_file_name)          
    
@transform(pepxml2csv, regex("pepxml2csv.ini_"), "fdr2probability.ini_")
def fdr2probability(input_file_name, output_file_name):
    wrap(Fdr2Probability,input_file_name, output_file_name)        

@transform(fdr2probability, regex("fdr2probability.ini_"), "proteinprophet.ini_") 
def proteinprophet(input_file_name, output_file_name):
    wrap(ProteinProphet,input_file_name, output_file_name)

@transform(proteinprophet, regex("proteinprophet.ini_"), "protxml2spectralcount.ini_") 
def protxml2spectralcount(input_file_name, output_file_name):
    wrap(ProtXml2SpectralCount,input_file_name, output_file_name)

@transform(protxml2spectralcount, regex("protxml2spectralcount.ini_"), "protxml2modifications.ini_")
def protxml2modifications(input_file_name, output_file_name):
    wrap(ProtXml2Modifications,input_file_name, output_file_name)

@transform(protxml2modifications, regex("protxml2modifications.ini_"), "protxml2openbis.ini_")
def protxml2openbis(input_file_name, output_file_name):
    wrap(ProtXml2Openbis,input_file_name, output_file_name)

@transform(protxml2openbis, regex("protxml2openbis.ini_"),"copy2dropbox.ini_")
def copy2dropbox(input_file_name, output_file_name):
    argv = ["", "-i", input_file_name, "-o",output_file_name]
    runner = IniFileRunner()
    application = Copy2IdentDropbox()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("copy2dropbox [%s]" % exit_code)  


pipeline_run([copy2dropbox], multiprocess = 16)
#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg