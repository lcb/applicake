#!/usr/bin/env python
'''

Created on May 22, 2012

@author: quandtan
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
from applicake.applications.os.echo import Echo
from applicake.applications.commons.collector import GuseCollector

cwd = None

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
    execute('rm *ini*')
#    execute('rm jobid.txt') 
    execute('rm flowchart.*')    
    with open("input.ini", 'w+') as f:
        f.write("""BASEDIR = %s
LOG_LEVEL = INFO
STORAGE = file
COMMENT = hallo,welt
DATASET_CODE = 20120320164249179-361885,20120320164249179-361886,20120320164249179-361887
""" % cwd)       

@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    sys.argv = ['IGNORED', '-i', input_file_name, '--GENERATORS', 'generate.ini' ,'-l','CRITICAL']
    runner = IniFileRunner()
    application = DatasetcodeGenerator()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
    
@transform(generator, regex("generate.ini_"), "echoout.ini_")
def echo(input_file_name, output_file_name):
    sys.argv = ['IGNORED', '-i', input_file_name, '-o', output_file_name, '--PREFIX', '/bin/echo','-l','CRITICAL']
    runner = WrapperRunner()
    wrapper = Echo()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("echo failed [%s]" % exit_code)   
    
@merge(echo, "output.ini")
def collector(notused_input_file_names, output_file_name):
    sys.argv = ['IGNORED', '--COLLECTORS', 'echoout.ini', '-o', output_file_name,'-s','file']
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("collector failed [%s]" % exit_code)    

pipeline_run([collector])
#pipeline_printout(sys.stdout, [collector], verbose=5)

#pipeline_printout_graph ('flowchart.png','png',[collector],no_key_legend = False) #svg
