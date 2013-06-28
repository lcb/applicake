#!/usr/bin/env python
'''
Created on Jul 11, 2012

@author: quandtan, wolski, blum
'''

import sys
import subprocess
import tempfile
from ruffus import *

from applicake.framework.runner import IniWrapperRunner, IniApplicationRunner
from applicake.applications.commons.collector import IniCollector
from applicake.framework.interfaces import IApplication, IWrapper

#workflow specific inputs 
from applicake.applications.commons.generator import IniDatasetcodeGenerator, IniParametersetGenerator
from applicake.applications.proteomics.openbis.dss import Dss
from applicake.applications.proteomics.openswath.parallel_splitdenoise import SplitDenoise
from applicake.applications.proteomics.openswath.parallel_rtnorm import OpenSwathRTNormalizerParallel
from applicake.applications.proteomics.openswath.parallel_analyzer import OpenSwathAnalyzerParallel
from applicake.applications.proteomics.openswath.mprophet import mProphet
from applicake.applications.proteomics.openswath.featurealign import FeatureAlignment
from applicake.applications.proteomics.openswath.openswathdropbox import Copy2SwathDropbox

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

    ######################START OF WF##############################


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        subprocess.call("rm *ini* *.err *.out", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
LOG_LEVEL = INFO
STORAGE = unchanged
THREADS = 8
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

IRTTRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_DIA_iRT.TraML"

DATASET_CODE = 20120713110650516-637617, 20120713005347029-637351
TRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_AQUASky_ShotgunLibrary_3t_345_sh.TraML"

SPACE = LOBLUM
PROJECT = TEST
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox

RUNDENOISER = false
WIDTH = 100
RTWIDTH = 9
EXTRACTION_WINDOW = 0.05
WINDOW_UNIT = Thomson
RT_EXTRACTION_WINDOW = 300
MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95
MIN_COVERAGE = 0.6
MPR_NUM_XVAL = 5
MPR_LDA_PATH = 
MPR_MAINVAR = xx_swath_prelim_score
MPR_VARS = bseries_score elution_model_fit_score intensity_score isotope_correlation_score isotope_overlap_score library_corr library_rmsd log_sn_score massdev_score massdev_score_weighted norm_rt_score xcorr_coelution xcorr_coelution_weighted xcorr_shape xcorr_shape_weighted yseries_score
FDR = 0.01
ALIGNER_MAX_RTDIFF = 30
ALIGNER_MAX_FDRQUAL = 0.2
ALIGNER_METHOD = best_overall
ALIGNER_REALIGNRUNS = true
ALIGNER_FRACSELECTED = 0
""")


@follows(setup)
@split("input.ini", "dssgenerator.ini_*")
def DSSgenerator(input_file_name, notused_output_file_names):
    wrap(IniDatasetcodeGenerator, input_file_name, 'dssgenerator.ini', ['--GENERATOR', 'dssgenerator.ini'])


@transform(DSSgenerator, regex("dssgenerator.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata', dir='.')
    wrap(Dss, input_file_name, output_file_name, ['--PREFIX', 'getmsdata', '--RESULT_FILE', tfile])


@transform(dss, regex("dss.ini_"), "splitwindows.ini_")
def splitwindows(input_file_name, output_file_name):
    wrap(SplitDenoise, input_file_name, output_file_name)


@transform(splitwindows, regex("splitwindows.ini_*"), "irt.ini_")
def irt(input_file_name, output_file_name):
    wrap(OpenSwathRTNormalizerParallel, input_file_name, output_file_name)


@transform(irt, regex("irt.ini_"), "openswathanalyzer.ini_")
def openswathanalyzer(input_file_name, output_file_name):
    wrap(OpenSwathAnalyzerParallel, input_file_name, output_file_name)


@transform(openswathanalyzer, regex("openswathanalyzer.ini_"), "mprophet.ini_")
def mprophet(input_file_name, output_file_name):
    wrap(mProphet, input_file_name, output_file_name)


@merge(mprophet, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    wrap(IniCollector, "mprophet.ini_0", output_file_name, ['--COLLECTOR', 'mprophet.ini'])


@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def paramgenerator(input_file_name, notused_output_file_names):
    wrap(IniParametersetGenerator, "collector.ini", "paramgenerate.ini", ['--GENERATOR', 'paramgenerate.ini'])


@transform(paramgenerator, regex("paramgenerate.ini_"), "featurealign.ini_")
def featurealign(input_file_name, output_file_name):
    wrap(FeatureAlignment, input_file_name, output_file_name)


@transform(featurealign, regex("featurealign.ini_"), "cp2dropbox.ini_")
def copytodropbox(input_file_name, output_file_name):
    wrap(Copy2SwathDropbox, input_file_name, output_file_name)

########################################################

pipeline_run([copytodropbox], multiprocess=2, verbose=3)
    
