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

import os
import sys
from ruffus import *
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.runner import IniFileRunner
from applicake.framework.runner import CollectorRunner
from applicake.framework.runner import WrapperRunner
from applicake.applications.commons.generator import DatasetcodeGenerator
from applicake.applications.proteomics.srm.anubis import Anubis
from applicake.framework.enums import KeyEnum
from applicake.applications.commons.collector import GuseCollector



cwd = None
IGNORED_PROC_NAME = "IGNORED_PROC_NAME"


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
    execute('rm *.ini*')
    execute('rm flowchart.*')    
    with open("input.ini", 'w+') as f:
        ini = "DATASET_CODE = 20120320164249179-361885\n"
        ini += "BASEDIR = /cluster/scratch/malars/workflows"
        ini += "%s = %i\n" % (Anubis.NULL_DIST_SIZE,      1000)
        ini += "%s = %i\n" % (Anubis.MAX_NUM_TRANSITIONS, 6)
        ini += "%s = %f\n" % (Anubis.PEAK_MIN_WIDTH,      0.1)
        ini += "%s = %s\n" % (Anubis.SINGLE_ANSWER,       "True")
        ini += "%s = %f\n" % (Anubis.P_VALUE_TOLERANCE,   0.01)
#        ini += "%s = %s\n" % (Anubis.OUTPUT_RESULT_FILE,  "ruffus_local.anubis")
        ini += "%s = %s\n" % (KeyEnum.MZML,               "101112_JT_pl2_03.mzML")
        ini += "%s = %s\n" % (Anubis.TRAML,               "final_method.ref")
        f.write(ini)       



@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    sys.argv    = [IGNORED_PROC_NAME, '-i', input_file_name, '--GENERATORS', 'generate.ini' ,'-l','CRITICAL']
    runner      = IniFileRunner()
    application = DatasetcodeGenerator()
    exit_code   = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 



@transform(generator, regex("generate.ini_"), "anubis-out.ini_")
def anubis(input_file_name, output_file_name):
    sys.argv    = [IGNORED_PROC_NAME, '-i', input_file_name, '-o', output_file_name, '-l','DEBUG', '-p']
    runner      = WrapperRunner()
    wrapper     = Anubis()
    exit_code   = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("anubis failed [%s]" % exit_code)       



pipeline_run([anubis])
#pipeline_printout(sys.stdout, [collector], verbose=5)
#pipeline_printout_graph ('flowchart.png', 'png', [collector], no_key_legend = False) #svg
