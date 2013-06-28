#!/usr/bin/env python
'''

Created on Oct 12, 2012

@author: johant,quandtan

This is simply a shallow conversion of the ruffus_local_echotest 
pipeline. It seems to work but likely some things can be made in
more appropriate ways.

What does the DatasetcodeGenerator do? The pipe wouldn't run without
the DATASET_CODE in the config, and the current value is simply 
the first from the echotest pipe. 

Another note: there is no TRAML value in KeyEnum, so I added it 
to Anubis. This should probably be moved to KeyEnum but I didn't
dare =).
'''

import sys
import subprocess
from ruffus import *

from applicake.framework.keys import Keys
from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.applications.commons.generator import IniDatasetcodeGenerator
from applicake.applications.proteomics.srm.anubis import Anubis


IGNORED_PROC_NAME = "IGNORED_PROC_NAME"
WORKFLOW = "WORKFLOW"

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
            ini = ""
            ini += "%s = %s\n" % (Keys.DATASET_CODE, '20120320164249179-361885')
            ini += "%s = %s\n" % (Keys.DATASET_DIR, './')
            ini += "%s = %s\n" % (Keys.BASEDIR, './')
            ini += "%s = %s\n" % (Keys.LOG_LEVEL, 'DEBUG')
            ini += "%s = %s\n" % (Keys.STORAGE, 'unchanged')
            ini += "%s = %s\n" % (Keys.WORKFLOW, 'anubis')
            ini += "%s = %s\n" % ('NULL_DIST_SIZE', '1000')
            ini += "%s = %s\n" % ('MAX_NUM_TRANSITIONS', '6,8')
            ini += "%s = %s\n" % ('PEAK_MIN_WIDTH', '0.1')
            ini += "%s = %s\n" % ('SINGLE_ANSWER', "True")
            ini += "%s = %s\n" % ('P_VALUE_TOLERANCE', '0.01')
            #        ini += "%s = %s\n" % (Anubis.OUTPUT_RESULT_FILE,  "ruffus_local.anubis")
            ini += "%s = %s\n" % (Keys.MZML, "101112_JT_pl2_03.mzML")
            ini += "%s = %s\n" % (Keys.TRAML, "final_method.ref")
            #        ini += "%s = %s\n" % (Anubis.LOG_DIR,             "./0/1/0/Anubis/log")
            f.write(ini)
    else:
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'


@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    wrap(IniDatasetcodeGenerator, input_file_name, "generator.ini", ['--GENERATOR', 'generate.ini', '-l', 'CRITICAL'])


@transform(generator, regex("generate.ini_"), "anubis.ini_")
def anubis(input_file_name, output_file_name):
    wrap(Anubis, input_file_name, output_file_name, ['-i', input_file_name, '-o', output_file_name, '-l', 'WARNING'])


pipeline_run([anubis])
#pipeline_printout(sys.stdout, [collector], verbose=5)
#pipeline_printout_graph ('flowchart.png', 'png', [collector], no_key_legend = False) #svg
