#!/usr/bin/env python
'''

Created on May 22, 2012

@author: loblum
'''

import os
import sys
import subprocess
from ruffus import *
from applicake.utils.drmaautils import DrmaaSubmitter


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.err *.out", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = %s
LOG_LEVEL = INFO
STORAGE = unchanged
COMMENT = hallo,welt
DATASET_CODE = 20120320164249179-361885,20120320164249179-361886,20120320164249179-361887
""" % os.getcwd())
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'


@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    submitter.run("run_dynrunner.py",
                  ['applicake.applications.commons.generator.IniDatasetcodeGenerator', '-i', input_file_name,
                   '--GENERATOR', 'generate.ini'])


@transform(generator, regex("generate.ini_"), "echoout.ini_")
def echo(input_file_name, output_file_name):
    submitter.run("run_dynrunner.py",
                  ['applicake.applications.os.echo.Echo', '-i', input_file_name, '-o', output_file_name])


@merge(echo, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    submitter.run("run_dynrunner.py",
                  ['applicake.applications.commons.collector.IniCollector', '-i', 'echoout.ini_0', '--COLLECTOR',
                   'echoout.ini', '-o', output_file_name])


@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def paramgenerate(input_file_name, output_file_name):
    submitter.run("run_dynrunner.py",
                  ['applicake.applications.commons.generator.IniParametersetGenerator', '-i', "collector.ini",
                   '--GENERATOR', 'paramgenerate.ini'])

###main###
print "Please put run_dynrunner.py in PATH!"
lsfargs = '-q pub.1h'
submitter = DrmaaSubmitter()
pipeline_run([paramgenerate], multiprocess=16)
print "IN CASE YOU SEE THIS WORKFLOW FINISHED SUCESSFULLY"