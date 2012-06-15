#!/usr/bin/env python
'''
Created on Jun 14, 2012

@author: quandtan
'''

import os
import sys
from ruffus import *
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.runner import GeneratorRunner
from applicake.framework.runner import CollectorRunner
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openbis.generator import GuseGenerator
from applicake.applications.os.echo import Echo
from applicake.applications.commons.collector import GuseCollector
from applicake.applications.proteomics.searchengine.xtandem import Xtandem
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.tpp.tandem2xml import Tandem2Xml
from applicake.applications.proteomics.tpp.xinteract import Xinteract
from applicake.applications.proteomics.tpp.interprophet import InterProphet
from applicake.applications.proteomics.openms.filehandling.idfileconverter import PepXml2IdXml
from applicake.applications.proteomics.openms.peptideproteinprocessing.falsediscoveryrate import FalseDiscoveryRate
from applicake.applications.proteomics.openms.peptideproteinprocessing.peptideindexer import PeptideIndexer
from applicake.applications.proteomics.openms.peptideproteinprocessing.idfilter import IdFilter
from applicake.applications.proteomics.openms.filehandling.fileconverter import MzXml2MzMl
from applicake.applications.proteomics.openms.signalprocessing.peakpickerhighres import PeakPickerHighRes
from applicake.applications.proteomics.openms.quantification.featurefindercentroided import FeatureFinderCentroided, OrbiLessStrict
from applicake.applications.proteomics.searchengine.omssa import Omssa
from applicake.applications.proteomics.proteowizard.msconvert import Mzxml2Mgf

cwd = None

def execute(command):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
    output, error = p.communicate()                                                                                                                                                                            
    out_stream = StringIO(output)
    err_stream = StringIO(error) 


def setup():
    cwd = '.'
    os.chdir(cwd)
    execute("find . -type d -iname '[0-9]*' -exec rm -rf {} \;")
    execute('rm *.err')
    execute('rm *.out')
    execute('rm *.log')
    execute('rm *ini*')
#    execute('rm jobid.txt') 
    execute('rm flowchart.*')    
    with open("input.ini", 'w+') as f:
        f.write("""BASEDIR = /cluster/scratch/malars/workflows
LOG_LEVEL = DEBUG
STORAGE = file
TEMPLATE = template.tpl
DATASET_DIR = /cluster/scratch/malars/datasets
DATASET_CODE = 20120124102254267-296925,
DBASE = /cluster/scratch/malars/biodb/ex_sp/20120301/decoy/ex_sp_9606.fasta
DECOY_STRING = DECOY_ 
FRAGMASSERR = 0.4
FRAGMASSUNIT = Da
PRECMASSERR = 15
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
STATIC_MODS = Carbamidomethyl (C)
VARIABLE_MODS = Oxidation (M)
THREADS = 4
XTANDEM_SCORE = k-score
XINTERACT_ARGS = -dDECOY_ -OAPdlIw
IPROPHET_ARGS = MINPROB=0
""" 
#,20120603165413998-510432,
# 20120606045538225-517638 -> b10-01219.p.mzxml
# 20120603160111752-510155 -> b10-01219.c.mzxml 
# 20120124102254267-296925 -> orbi silac hela from petriimport os
)       
        

@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    sys.argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini' ,'-l','DEBUG']
    runner = GeneratorRunner()
    application = GuseGenerator()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
    
@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name, '--PREFIX', 'getmsdata']
    runner = WrapperRunner()
    wrapper = Dss()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
                raise Exception("[%s] failed [%s]" % ('dss',exit_code))    

@transform(dss, regex("dss.ini_"), "msconvert.ini_")
def msconvert(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name, 
                '-l','DEBUG']
    runner = WrapperRunner()
    wrapper = Mzxml2Mgf()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('msconvert',exit_code))


    
@transform(msconvert, regex("msconvert.ini_"), "omssa.ini_")
def omssa(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name, 
                '-l','DEBUG']
    runner = WrapperRunner()
    wrapper = Omssa()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('omssa',exit_code))

@transform(omssa, regex("omssa.ini_"), "xinteract.ini_")
def xinteract(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,
                '-l','DEBUG'
                ]
    runner = WrapperRunner()
    wrapper = Xinteract()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('xinteract',exit_code))  
    
pipeline_run([xinteract])

#pipeline_printout_graph ('flowchart.png','png',[collector],no_key_legend = False) #svg
