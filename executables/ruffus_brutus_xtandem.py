#!/usr/bin/env python
'''
Created on Jun 5, 2012

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
from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mgf
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.tpp.tandem2xml import Tandem2Xml
from applicake.applications.proteomics.tpp.xinteract import Xinteract
from applicake.applications.proteomics.tpp.interprophet import InterProphet
from applicake.applications.proteomics.openms.filehandling.idfileconverter import PepXml2IdXml
from applicake.applications.proteomics.openms.peptideproteinprocessing.falsediscoveryrate import FalseDiscoveryRate

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
DATASET_CODE = 20120603160111752-510155,
DBASE = /cluster/scratch/malars/biodb/ex_sp/current/decoy/ex_sp_9606.fasta
FRAGMASSERR = 0.4
FRAGMASSUNIT = Da
PRECMASSERR = 15
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
STATIC_MODS = Carbamidomethyl (C)
VARIABLE_MODS = Oxidation (M)
THREADS = 8
XTANDEM_SCORE = k-score
XINTERACT_ARGS = -dDECOY_ -OAPdlIw
IPROPHET_ARGS = MINPROB=0
""" #,20120603165413998-510432,
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
    
@transform(dss, regex("dss.ini_"), "xtandem.ini_")
def tandem(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name, 
                '--TEMPLATE', 'xtandem.tpl',
                '-l','DEBUG']
    runner = WrapperRunner()
    wrapper = Xtandem()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('tandem',exit_code))

@transform(tandem, regex("xtandem.ini_"), "xtandem2xml.ini_")
def tandem2xml(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name
                ,'-l','DEBUG']
    runner = WrapperRunner()
    wrapper = Tandem2Xml()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('tandem2xml',exit_code))      

@transform(tandem2xml, regex("xtandem2xml.ini_"), "xinteract.ini_")
def xinteract(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,
                '-l','DEBUG'
                ]
    runner = WrapperRunner()
    wrapper = Xinteract()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('xinteract',exit_code))    

    
@merge(xinteract, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    sys.argv = ['', '--COLLECTORS', 'xinteract.ini', '-o', output_file_name,'-s','file']
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('collector',exit_code))    

@transform(collector,regex('collector.ini'),'interprophet.ini')
def interprophet(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,'-s','file',                
                ]
    runner = WrapperRunner()
    application = InterProphet()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('iprophet',exit_code))     


@transform(interprophet,regex('interprophet.ini'),'pepxml2idxml.ini')
def pepxml2idxml(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,'-s','file',                
                ]
    runner = WrapperRunner()
    application = PepXml2IdXml()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('pepxml2idxml',exit_code)) 


@transform(pepxml2idxml,regex('pepxml2idxml.ini'),'fdr.ini')
def fdr(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,'-s','file',                
                ]
    runner = WrapperRunner()
    application = FalseDiscoveryRate()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('fdr',exit_code)) 

pipeline_run([pepxml2idxml])


#pipeline_printout_graph ('flowchart.png','png',[collector],no_key_legend = False) #svg
