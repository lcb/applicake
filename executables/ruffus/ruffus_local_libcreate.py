#!/usr/bin/env python
'''
Created on Oct 18, 2012

@author: quandtan, loblum
'''

import sys
import subprocess
import tempfile

from ruffus import *

from applicake.applications.proteomics.openbis.processexperiment import ProcessExperiment
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner
from applicake.applications.commons.generator import IniDatasetcodeGenerator, \
    IniParametersetGenerator
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.libcreation.spectrast import RawlibNodecoy, RTcalibNoirt
from applicake.applications.proteomics.libcreation.spectrast2tsv2traml import Spectrast2TSV2traML
from applicake.applications.proteomics.libcreation.spectrastirtcalibrator import SpectrastIrtCalibrator
from applicake.applications.proteomics.libcreation.libcreatedropbox import Copy2LibcreateDropbox
from applicake.applications.commons.collector import IniCollector


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
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.err *.out", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox

LOG_LEVEL = INFO
STORAGE = unchanged
WORKFLOW = traml_create

EXPERIMENT = E287786
DATASET_CODE = 20120320163951515-361883, 20120320163653755-361882, 20120320164249179-361886
PEPTIDEFDR = 0.01

COMMENT = newUPS1
DESCRIPTION = newUPS measurement 3 technical replicates
MS_TYPE = CID-QTOF

RSQ_THRESHOLD = 0.95
RTKIT = 
APPLYCHAUVENET = False
PRECURSORLEVEL = False
SPECTRALEVEL = False
TSV_MASS_LIMITS = 400-2000
TSV_ION_LIMITS = 2-6
TSV_PRECISION = 0.05
TSV_CHARGE = 1;2
TSV_REMOVE_DUPLICATES = True 
TSV_EXACT = False
TSV_GAIN =  
TSV_SERIES = 
CONSENSUS_TYPE = Consensus
RUNRT = True

""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'


@follows(setup)
@files('input.ini', 'getexperiment.ini')
def getexperiment(input_file_name, output_file_name):
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getexperiment'])


@follows(getexperiment)
@files('getexperiment.ini', 'processexperiment.ini')
def processexperiment(input_file_name, output_file_name):
    wrap(ProcessExperiment, input_file_name, output_file_name)


@follows(processexperiment)
@split('processexperiment.ini', "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    wrap(IniDatasetcodeGenerator, input_file_name, "generate.ini", ['--GENERATOR', 'generate.ini'])


@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata', dir='.')
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getmsdata', '--RESULT_FILE', tfile])


@merge(dss, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    wrap(IniCollector, "dss.ini_0", output_file_name, ['--COLLECTOR', 'dss.ini'])


@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def paramgenerator(input_file_name, notused_output_file_names):
    wrap(IniParametersetGenerator, input_file_name, "paramgenerate.ini", ['--GENERATOR', 'paramgenerate.ini'])


@transform(paramgenerator, regex('paramgenerate.ini_'), 'rawlibnodecoy.ini_')
def rawlibnodecoy(input_file_name, output_file_name):
    wrap(RawlibNodecoy, input_file_name, output_file_name)

#########OPTIONAL################

@transform(rawlibnodecoy, regex('rawlibnodecoy.ini_'), 'irtcalibration.ini_')
def irtcalibration(input_file_name, output_file_name):
    wrap(SpectrastIrtCalibrator, input_file_name, output_file_name)


@transform(irtcalibration, regex('irtcalibration.ini_'), 'rtcalibnoirt.ini_')
def rtcalibnoirt(input_file_name, output_file_name):
    wrap(RTcalibNoirt, input_file_name, output_file_name)


#########DONE BY DEFAULT########################
@transform(rtcalibnoirt, regex('rtcalibnoirt.ini_'), 'spectrast2traml.ini_')
def spectrast2traml(input_file_name, output_file_name):
    wrap(Spectrast2TSV2traML, input_file_name, output_file_name)

@transform(spectrast2traml, regex('spectrast2traml.ini_'), 'copy2dropbox.ini_')
def copy2box(input_file_name, output_file_name):
    wrap(Copy2LibcreateDropbox, input_file_name, output_file_name)


pipeline_run([copy2box], verbose=2, multiprocess=8)
