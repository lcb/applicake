#!/usr/bin/env python
'''
Created on Aug 13, 2012

@author: quandtan
'''

import sys
import subprocess
import tempfile

from ruffus import *
from applicake.applications.proteomics.openbis.biopersdb import BioPersonalDB

from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner
from applicake.applications.commons.generator import IniDatasetcodeGenerator, \
    IniParametersetGenerator
from applicake.applications.os.echo import Echo
from applicake.applications.commons.collector import IniCollector
from applicake.applications.proteomics.tpp.enginecollector import IniEngineCollector
from applicake.applications.proteomics.tpp.searchengines.xtandem import Xtandem
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.tpp.interprophet import InterProphet
from applicake.applications.proteomics.tpp.proteinprophetFDR import ProteinProphetFDR
from applicake.applications.proteomics.tpp.protxml2openbissequence import ProtXml2OpenbisSequence
from applicake.applications.proteomics.tpp.tppdropbox import Copy2IdentDropbox
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.tpp.searchengines.omssa import Omssa
from applicake.applications.proteomics.tpp.searchengines.myrimatch import Myrimatch
from applicake.applications.proteomics.tpp.peptideprophetsequence import PeptideProphetSequence


#helper function
def wrap(applic, input_file_name, output_file_name, opts=None):
    argv = ['-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    application = applic()
    if isinstance(application, IApplication):
        runner = IniApplicationRunner()
    elif isinstance(application, IWrapper):
        runner = IniWrapperRunner()
    else:
        raise Exception('could not identfy runner for [%s]' % applic.__name__)
    application = applic()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % (applic.__name__, exit_code))


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        subprocess.call("rm *ini* *.err *.out", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""DATASET_CODE = 20120320163951515-361883, 20120320163653755-361882, 20120320164249179-361886
PRECMASSERR = 15
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
STORAGE = unchanged
FDR = 0.01
RUNTANDEM = True
PRECMASSUNIT = ppm
COMMENT = TPP of UPS1 ruffus
RUNMYRIMATCH = True
LOG_LEVEL = INFO
MISSEDCLEAVAGE = 1
FRAGMASSERR = 0.4
WORKFLOW = TPP_ruffus
DB_SOURCE = PersonalDB
DBASE = PERSONAL_DB-BEHULLAR-LOBLUM_UPS1-972
#DBASE = /cluster/scratch_xl/shareholder/imsb_ra/bin/newbiodb/data/ex_pd/current/decoy/loblum_UPS1_iRT.fasta
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/drop-box_prot_ident
DATABASE_VERSION = 20130117
XTANDEM_SCORE = k-score
SPACE = LOBLUM
DECOY_STRING = DECOY_
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows/
PROJECT = TEST
STATIC_MODS = Carbamidomethyl (C)
DATABASE_PACKAGE = ex_pd
XINTERACT_ARGS = -dDECOY_ -OAPdlIw (dummy)
DATABASE_DB = loblum_UPS1_iRT
FRAGMASSUNIT = Da
ENZYME = Trypsin
IPROPHET_ARGS = MINPROB=0
RUNOMSSA = True
THREADS = 4"""
                #,20120603165413998-510432,
                # 20120606045538225-517638 -> b10-01219.p.mzxml
                # 20120603160111752-510155 -> b10-01219.c.mzxml
                # 20120124102254267-296925,20120124121656335-296961 -> orbi silac hela from petri
            )


@follows(setup)
@files("input.ini","biopersdb.ini")
def biopersdb(input_file_name,output_file_name):
    wrap(BioPersonalDB,input_file_name,output_file_name)

@follows(biopersdb)
@split("biopersdb.ini", "generate.ini_*")
def datasetSplit(input_file_name, notused_output_file_names):
    wrap(IniDatasetcodeGenerator, input_file_name, "output.ini", ['--GENERATOR', 'generate.ini'])


@transform(datasetSplit, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    _, tfile = tempfile.mkstemp(suffix='.out', prefix='getdataset', dir='.')
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getmsdata','--RESULT_FILE', tfile])


@transform(dss, regex("dss.ini_"), "engineSplit.ini_")
def engineSplit(input_file_name, output_file_name):
    print "NOT A CONDITIONAL WORKFLOW!!!"
    wrap(Echo, input_file_name, output_file_name, ['--PREFIX', '/bin/echo'])

##################################################################################

@transform(engineSplit, regex("engineSplit.ini_"), "xtandem.ini_")
def tandem(input_file_name, output_file_name):
    wrap(Xtandem, input_file_name, output_file_name, ['--PREFIX', 'tandem.exe'])

@transform(tandem, regex("xtandem.ini_"), "tandem.ini_")
def pepprotandem(input_file_name, output_file_name):
    wrap(PeptideProphetSequence, input_file_name, output_file_name, ['-n', 'peptandem'])

##################################################################################

@transform(engineSplit, regex("engineSplit.ini_"), "omssarun.ini_")
def omssa(input_file_name, output_file_name):
    wrap(Omssa, input_file_name, output_file_name)


@transform(omssa, regex("omssarun.ini_"), "omssa.ini_")
def pepproomssa(input_file_name, output_file_name):
    wrap(PeptideProphetSequence, input_file_name, output_file_name, ['-n', 'pepomssa', '--OMSSAFIX'])

###################################################################################


@transform(engineSplit, regex("engineSplit.ini_"), "myri.ini_")
def myrimatch(input_file_name, output_file_name):
    wrap(Myrimatch, input_file_name, output_file_name)


@transform(myrimatch, regex("myri.ini_"), "myrimatch.ini_")
def peppromyri(input_file_name, output_file_name):
    wrap(PeptideProphetSequence, input_file_name, output_file_name, ['-n', 'pepmyri'])


############################# MERGE SEARCH ENGINE RESULTS ################################## 
#.*_(.+)$ = any char any no. times, underscore, "group" with at least one char, end of line  
#"groups" are acessible with \n afterwards (.* is not a group!)
@collate([pepprotandem,pepproomssa,peppromyri],regex(r".*_(.+)$"),  r'mergeengine.ini_\1')
def mergeEngines(input_file_names, output_file_name):
    wrap(IniEngineCollector, 'output.ini', 'mergeengine.ini',
         ['--GENERATOR', 'mergeengine.ini', '--ENGINES', 'tandem', '--ENGINES', 'myrimatch', '--ENGINES', 'omssa'])

@transform(mergeEngines, regex("mergeengine.ini_"), "interprophetengines.ini_")
def interprophetengines(input_file_name, output_file_name):
    wrap(InterProphet, input_file_name, output_file_name,['-n', 'iproengine'])


############################# TAIL: PARAMGENERATE ##################################   

@merge(interprophetengines, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    wrap(IniCollector, "interprophetengines.ini_0", output_file_name, ['--COLLECTOR', 'interprophetengines.ini'])


@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def parameterSplit(input_file_name, notused_output_file_names):
    wrap(IniParametersetGenerator, "collector.ini", "output2.ini", ['--GENERATOR', 'paramgenerate.ini'])


@transform(parameterSplit, regex("paramgenerate.ini_"), "interprophetparam.ini_")
def interprophetParam(input_file_name, output_file_name):
    wrap(InterProphet, input_file_name, output_file_name, ['-n', 'iproparam'])


@transform(interprophetParam, regex("interprophetparam.ini_"), "proteinprophet.ini_")
def proteinprophet(input_file_name, output_file_name):
    wrap(ProteinProphetFDR, input_file_name, output_file_name)


@transform(proteinprophet, regex("proteinprophet.ini_"), "protxml2openbis.ini_")
def protxml2openbis(input_file_name, output_file_name):
    wrap(ProtXml2OpenbisSequence, input_file_name, output_file_name)


@transform(protxml2openbis, regex("protxml2openbis.ini_"), "copy2dropbox.ini_")
def copy2dropbox(input_file_name, output_file_name):
    wrap(Copy2IdentDropbox, input_file_name, output_file_name)


pipeline_run([copy2dropbox], multiprocess=9)

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
