#!/usr/bin/env python
'''

Created on May 22, 2012

@author: quandtan
'''

import sys
import subprocess
from ruffus import *
from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner
from applicake.framework.interfaces import IApplication, IWrapper

from applicake.applications.proteomics.sequestimport.sequestgenerator import SequestGenerator
from applicake.applications.proteomics.tpp.peptideprophetsequence import PeptideProphetSequence
from applicake.applications.commons.generator import IniParametersetGenerator
from applicake.applications.commons.collector import IniCollector
from applicake.applications.proteomics.tpp.interprophet import InterProphet
from applicake.applications.proteomics.tpp.proteinprophetFDR import ProteinProphetFDR
from applicake.applications.proteomics.tpp.protxml2openbissequence import ProtXml2OpenbisSequence
from applicake.applications.proteomics.tpp.tppdropbox import Copy2IdentDropbox




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
        raise Exception('didnt find runner for [%s]' % applic.__name__)
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % (applic.__name__, exit_code))


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.err *.out", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""
            WORKFLOW = sequest_import_ruffus
SEQUESTHOST = 1
SEQUESTRESULTPATH = 475
FDR = 0.01
IPROPHET_ARGS = MINPROB=0
XINTERACT = -dDECOY_ -OAPdlIw (dummy)
LOG_LEVEL = INFO
STORAGE = unchanged
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows/
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/drop-box_prot_ident
USERNAME = loblum
DECOY_STRING = DECOY_
SPACE = LOBLUM
PROJECT = TEST
COMMENT = direct sequest
""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'


@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(infile, outfile):
    wrap(SequestGenerator, infile, 'generate.ini', ['--GENERATOR', 'generate.ini'])


@transform(generator, regex("generate.ini_"), "peppro.ini_")
def peppro(input_file_name, output_file_name):
    wrap(PeptideProphetSequence, input_file_name, output_file_name)


@merge(peppro, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    wrap(IniCollector, "peppro.ini_0", output_file_name, ['--COLLECTOR', 'peppro.ini'])


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


pipeline_run([copy2dropbox], multiprocess=3)
