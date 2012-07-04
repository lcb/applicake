#!/usr/bin/env python
'''
Created on Jun 24, 2012

@author: quandtan
'''
import os
import sys
from ruffus import *
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.runner import IniFileRunner, ApplicationRunner
from applicake.framework.runner import CollectorRunner
from applicake.framework.runner import WrapperRunner
from applicake.applications.commons.generator import DatasetcodeGenerator
from applicake.applications.os.echo import Echo
from applicake.applications.commons.collector import GuseCollector
from applicake.applications.proteomics.searchengine.xtandem import Xtandem
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.tpp.tandem2xml import Tandem2Xml
from applicake.applications.proteomics.tpp.xinteract import Xinteract
from applicake.applications.proteomics.tpp.interprophet import InterProphet
from applicake.applications.proteomics.openms.filehandling.idfileconverter import PepXml2IdXml,\
    IdXml2PepXml
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
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox
from applicake.applications.commons.inifile import Unifier
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.searchengine.myrimatch import Myrimatch
from applicake.applications.proteomics.openms.identification.macotadapteronline import MascotAdapterOnline

cwd = None


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
        msg = 'could not identfy runner with applic [%s] and argv [%s]' % (applic.__name__,argv)
        print msg
        raise Exception(msg)    
    application = applic()
    exit_code = runner(argv, application)
    if exit_code != 0:
        print 'use runner of type [%s] with applic [%s] and argv [%s]' % (runner.__class__.__name__,applic.__name__,argv)
        raise Exception("[%s] failed [%s]" % (applic.__name__, exit_code)) 

def execute(command):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
    output, error = p.communicate()                                                                                                                                                                              
    out_stream = StringIO(output)
    err_stream = StringIO(error) 



def mascotadapteronline():
    wrap(MascotAdapterOnline,'mzxml2mzml.ini','mascotadapteronline.ini',['--MASCOT_HOSTNAME','imsb-ra-mascot.ethz.ch','--MASCOT_USERNAME','bla','--MASCOT_PASSWORD','blabla','-p'])

@follows(mascotadapteronline)
def idxml2pepxml():
    wrap(IdXml2PepXml,'mascotadapteronline.ini','idxml2pepxml.ini',['-p'])



#pipeline_run([idxml2pepxml])


@follows(idxml2pepxml)
def xinteract():
    wrap(Xinteract,'idxml2pepxml.ini','xinteract.ini')   

@follows(xinteract)
def interprophet():
    wrap(InterProphet,'xinteract.ini','interprophet.ini')    

@follows(interprophet)
def pepxml2csv():
    wrap(Pepxml2Csv,'interprophet.ini','pepxml2csv.ini')   
    
@follows(pepxml2csv)
def fdr2probability():
    wrap(Fdr2Probability,'pepxml2csv.ini','fdr2probability.ini')         

@follows(fdr2probability)
def proteinprophet():
    wrap(ProteinProphet,'fdr2probability.ini','proteinprophet.ini') 

@follows(proteinprophet)
def protxml2spectralcount():
    wrap(ProtXml2SpectralCount,'proteinprophet.ini','protxml2spectralcount.ini') 

@follows(protxml2spectralcount)
def protxml2modifications():
    wrap(ProtXml2Modifications,'protxml2spectralcount.ini','protxml2modifications.ini') 

@follows(protxml2modifications)
def protxml2openbis():
    wrap(ProtXml2Openbis,'protxml2modifications.ini','protxml2openbis.ini') 

@follows(protxml2openbis)
def copy2dropbox():
    wrap(Copy2Dropbox,'protxml2openbis.ini','copy2dropbox.ini') 

#@follows()
#def ():
#    wrap(,'','') 
#    @follows()
#def ():
#    wrap(,'','') 
#    @follows()
#def ():
#    wrap(,'','')     




pipeline_run([copy2dropbox])
#pipeline_run([featurefindercentroided])


#pipeline_printout_graph ('flowchart.png','png',[collector],no_key_legend = False) #svg

