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
from applicake.framework.runner import *
from applicake.applications.commons.generator import IniDatasetcodeGenerator, \
    IniParametersetGenerator
from applicake.framework.interfaces import IApplication, IWrapper

from applicake.applications.proteomics.lfq.annotxmlfromcsv import AnnotProtxmlFromUpdatedCsv
from applicake.applications.proteomics.lfq.lfqpart1 import LFQpart1
from applicake.applications.proteomics.lfq.lfqpart2 import LFQpart2
from applicake.applications.proteomics.lfq.lfqdropbox import Copy2QuantDropbox
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
WORKFLOW = LFQ_110_2013-03-27-075655_20130611143648273
COMMENT = test iupdate -  | started 13-06-11 14:36
LOG_LEVEL = INFO
STORAGE = unchanged

BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows/
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/drop-box_prot_quant

PEPTIDEFDR = 0.01
FEATUREFINDER_MASS_TRACE__MZ_TOLERANCE = 0.03
FEATUREFINDER_MASS_TRACE__MIN_SPECTRA = 10
FEATUREFINDER_MASS_TRACE__MAX_MISSING = 1
FEATUREFINDER_MASS_TRACE__SLOPE_BOUND = 0.1
FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_LOW = 1
FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_HIGH = 4
FEATUREFINDER_ISOTOPIC_PATTERN__MZ_TOLERANCE = 0.03
FEATUREFINDER_SEED__MIN_SCORE = 0.8
FEATUREFINDER_FEATURE__MIN_SCORE = 0.7
FEATUREFINDER_FEATURE__MIN_ISOTOPE_FIT = 0.8
FEATUREFINDER_FEATURE__MIN_TRACE_SCORE = 0.5
FEATURELINKER_DISTANCE_RT__MAX_DIFFERENCE = 100
FEATURELINKER_DISTANCE_MZ__MAX_DIFFERENCE = 0.3
FEATURELINKER_DISTANCE_MZ__UNIT = Da
IDMAPPER_RT_TOLERANCE = 5
IDMAPPER_MZ_TOLERANCE = 20
IDMAPPER_MZ_REFERENCE = precursor
IDMAPPER_USE_CENTROID_MZ = false
POSECLUSTERING_MZ_PAIR_MAX_DISTANCE = 0.5
POSECLUSTERING_DISTANCE_MZ_MAX_DIFF = 0.3
POSECLUSTERING_DISTANCE_RT_MAX_DIFF = 100
PEAKPICKER_SIGNAL_TO_NOISE = 4
PEAKPICKER_MS1_ONLY = false
PROTEINQUANTIFIER_TOP = 0
PROTEINQUANTIFIER_AVERAGE = median
PROTEINQUANTIFIER_INCLUDE_ALL = true

SPACE = LOBLUM
PROJECT = TEST

EXPERIMENT = E20130226_161138_103439_0
DATASET_CODE = 20110721034730308-201103, 20110721173145616-201355, 20110722014852343-201543, 20110721054532782-201128, 20110721210947748-201441, 20110721233250123-201503, 20110721073234274-201170, 20110722033454238-201588
""")
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'


@follows(setup)
@files('input.ini', 'getexperiment.ini')
def getexperiment(input, output):
    wrap(Dss, input, output, ['--PREFIX', 'getexperiment'])


@follows(getexperiment)
@files('getexperiment.ini', 'processexperiment.ini')
def processexperiment(input, output):
    wrap(ProcessExperiment, input, output)

################################################################################################

@follows(processexperiment)
@split('processexperiment.ini', "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    wrap(IniDatasetcodeGenerator, input_file_name, "generate.ini", ['--GENERATOR', 'generate.ini'])


@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata', dir='.')
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getmsdata', '--RESULT_FILE', tfile])


@transform(dss, regex("dss.ini_"), "lfqpart1.ini_")
def lfqpart1(input_file_name, output_file_name):
    wrap(LFQpart1, input_file_name, output_file_name)


@merge(lfqpart1, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    wrap(IniCollector, "lfqpart1.ini_0", output_file_name, ['--COLLECTOR', 'lfqpart1.ini'])

################################################################################################

@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def parameterSplit(input_file_name, notused_output_file_names):
    wrap(IniParametersetGenerator, "collector.ini", "paramgenerate.ini", ['--GENERATOR', 'paramgenerate.ini'])


@transform(parameterSplit, regex("paramgenerate.ini_"), "lfqpart2.ini_")
def lfqpart2(input_file_name, output_file_name):
    wrap(LFQpart2, input_file_name, output_file_name)


@transform(lfqpart2, regex("lfqpart2.ini_"), "annotxml.ini_")
def annotxml(input_file_name, output_file_name):
    wrap(AnnotProtxmlFromUpdatedCsv, input_file_name, output_file_name)


@transform(annotxml, regex("annotxml.ini_"), "cp2dropbox.ini_")
def cp2dropbox(input_file_name, output_file_name):
    wrap(Copy2QuantDropbox, input_file_name, output_file_name)

################################################################################################
#resourcetests | old set        | PA1         | oldUPS      | carone      | olga        | newset
#part1 pp-ff   | 8h 9Gram 9Gscr | 2.0Gs 1700r | 3.8Gs 5881r | 7.1Gs 2672r | 4.6Gs 2738r | 8h 6000ram 8000scr
#part2 ma-fl   | 36h 8Gr 16Gs   | 66s 1411r   | 833s 2353r  | 2.1Gs 3518r | 1.8Gs 3400r | 36h 4000ram 4000scr   

pipeline_run([cp2dropbox], multiprocess=2)
#pipeline_printout_graph ('flowchart.png','png',[idfilter],no_key_legend = False) #svg
