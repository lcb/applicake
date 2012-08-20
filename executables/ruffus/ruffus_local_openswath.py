#!/usr/bin/env python
'''
Created on Jul 11, 2012

@author: quandtan
'''



import os
import sys
import subprocess

from ruffus import *

from applicake.framework.runner import IniFileRunner2, ApplicationRunner, CollectorRunner, WrapperRunner, IniFileRunner
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.proteomics.openswath.chromatogramextractor import ChromatogramExtractor
from applicake.applications.proteomics.openswath.mrmrtnormalizer import MRMRTNormalizer
from applicake.applications.proteomics.openswath.mrmanalyzer import MRMAnalyzer
from applicake.applications.proteomics.openswath.featurexmltotsv import FeatureXMLToTSV
from applicake.applications.proteomics.openswath.FileMerger import FileMerger
from applicake.applications.proteomics.openswath.KeySwitcher import KeySwitcher
from applicake.applications.proteomics.openswath.SwathGenerator import SwathGenerator

cwd = None


#helper function
def wrap(applic, input_file_name, output_file_name, opts=None):
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
    subprocess.call("rm *ini* *.err *.out *.log ",shell=True)
    with open("input.ini", 'w+') as f:
        f.write("""BASEDIR = /cluster/scratch/malars/loblum/openswathtest/workflows
LOG_LEVEL = DEBUG
STORAGE = memory_all
THREADS = 8
MZMLGZDIR = /cluster/scratch/malars/loblum/openswathtest/datasets
IRTTRAML = "/cluster/scratch/malars/loblum/openswathtest/tramls/DIA_iRT.TraML"
TRAML = "/cluster/scratch/malars/loblum/openswathtest/tramls/AQUA4_sh_new.TraML"
MIN_UPPER_EDGE_DIST = 1
MIN_RSQ = 0.95
MIN_COVERAGE = 0.6
"""
)       
        
@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini']
    runner = IniFileRunner()
    application = SwathGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 


@transform(generator, regex("generate.ini_"), "chromatogramextractor.ini_")
def chromatogramextractor(input_file_name, output_file_name):
    wrap(ChromatogramExtractor, input_file_name, output_file_name) 


@follows(chromatogramextractor)
def filemerger():
    wrap(FileMerger, 'chromatogramextractor.ini_0', 'filemerger.ini')
    
@follows(filemerger)
def mrmrtnormalizer():
    wrap(MRMRTNormalizer, 'filemerger.ini', 'mrmrtnormalizer.ini', ['-p'])

@follows(mrmrtnormalizer)
def keyswitcher():
    wrap(KeySwitcher, "mrmrtnormalizer.ini", "keyswitcher.ini")

@follows(keyswitcher)
@split("input.ini", "generate2.ini_*")
def generator2(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini','-o','generator.ini','-l','DEBUG']
    runner = IniFileRunner()
    application = SwathGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 

@transform(generator2, regex("generate2.ini_"), "chromatogramextractor2.ini_")
def chromatogramextractor2(input_file_name, output_file_name):
    wrap(ChromatogramExtractor, input_file_name, output_file_name, ['-p']) 

@transform(chromatogramextractor2, regex("chromatogramextractor2.ini_"), "mrmanalyzer.ini_")
def mrmanalyzer(input_file_name, output_file_name):
    wrap(MRMAnalyzer, input_file_name, output_file_name, ['-p']) 

@transform(mrmanalyzer,regex("mrmanalyzer.ini_"), "featurexml2tsv.ini_")
def featurexmltotsv(input_file_name, output_file_name):
    wrap(FeatureXMLToTSV, input_file_name, output_file_name, ['-p']) 

pipeline_run([featurexmltotsv], multiprocess=2)
