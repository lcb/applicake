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
from applicake.applications.proteomics.sybit.pepxml2csv import Pepxml2Csv
from applicake.applications.proteomics.sybit.fdr2probability import Fdr2Probability
from applicake.applications.proteomics.tpp.proteinprophet import ProteinProphet
from applicake.applications.proteomics.sybit.protxml2spectralcount import ProtXml2SpectralCount
from applicake.applications.proteomics.sybit.protxml2modifications import ProtXml2Modifications
from applicake.applications.proteomics.sybit.protxml2openbis import ProtXml2Openbis

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
DBASE = /cluster/scratch/malars/biodb/ex_sp/current/decoy/ex_sp_9606.fasta
DECOY_STRING = DECOY_ 
FRAGMASSERR = 0.4
FRAGMASSUNIT = Da
PRECMASSERR = 15
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
ENZYME = Trypsin
STATIC_MODS = Carbamidomethyl (C)
THREADS = 4
XTANDEM_SCORE = k-score
XINTERACT_ARGS = -dDECOY_ -OAPdlIw
IPROPHET_ARGS = MINPROB=0
FDR=0.01
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
    
@transform(dss, regex("dss.ini_"), "xtandem.ini_")
def tandem(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name, 
                '--PREFIX', 'tandem.exe','-s','file','-l','DEBUG']
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

@follows(collector)
def interprophet():
    sys.argv = ['', '-i', 'collector.ini', '-o', 'interprophet.ini']
    runner = WrapperRunner()
    application = InterProphet()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('iprophet',exit_code))     


@transform(interprophet,regex('interprophet.ini'),'pepxml2csv.ini')
def pepxml2csv(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = Pepxml2Csv()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('pepxml2csv',exit_code))   

@transform(pepxml2csv,regex('pepxml2csv.ini'),'fdr2probability.ini')
def fdr2probability(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = Fdr2Probability()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('fdr2probability',exit_code))  
    
    
@transform(fdr2probability,regex('fdr2probability.ini'),'proteinprophet.ini')
def proteinprophet(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = ProteinProphet()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('proteinprophet',exit_code))      


@transform(proteinprophet,regex('proteinprophet.ini'),'protxml2spectralcount.ini')
def protxml2spectralcount(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = ProtXml2SpectralCount()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('protxml2spectralcount',exit_code))

@transform(protxml2spectralcount,regex('protxml2spectralcount.ini'),'protxml2modifications.ini')
def protxml2modifications(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,'-p']
    runner = WrapperRunner()
    application = ProtXml2Modifications()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('protxml2modifications',exit_code))

@transform(protxml2modifications,regex('protxml2modifications.ini'),'.ini')
def protxml2openbis(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = ProtXml2Openbis()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('protxml2openbis',exit_code))


@transform(interprophet,regex('interprophet.ini'),'pepxml2idxml.ini')
def pepxml2idxml(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = PepXml2IdXml()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('pepxml2idxml',exit_code)) 

@transform(pepxml2idxml,regex('pepxml2idxml.ini'),'peptideindexer.ini')
def peptideindexer(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = PeptideIndexer()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('peptideindexer',exit_code))

@transform(peptideindexer,regex('peptideindexer.ini'),'fdr.ini')
def fdr(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = FalseDiscoveryRate()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('fdr',exit_code)) 
    
@transform(fdr,regex('fdr.ini'),'idfilter.ini')
def idfilter(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = IdFilter()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('idfilter',exit_code)) 
    
@transform(idfilter,regex('idfilter.ini'),'mzxml2mzml.ini')
def mzxml2mzml(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
    application = MzXml2MzMl()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('mzxml2mzml',exit_code)) 

@transform(mzxml2mzml,regex('mzxml2mzml.ini'),'peakpickerhighres.ini')
def peakpickerhighres(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,'--SIGNAL_TO_NOISE','1']
    runner = WrapperRunner()
    application = PeakPickerHighRes()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('peakpickerhighres',exit_code)) 
         
@transform(peakpickerhighres,regex('peakpickerhighres.ini'),'featurefindercentroided.ini')
def featurefindercentroided(input_file_name, output_file_name):
    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
    runner = WrapperRunner()
#    application = FeatureFinderCentroided()
    application = OrbiLessStrict()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('featurefindercentroided',exit_code)) 
         

pipeline_run([protxml2openbis])
#pipeline_run([featurefindercentroided])


#pipeline_printout_graph ('flowchart.png','png',[collector],no_key_legend = False) #svg
