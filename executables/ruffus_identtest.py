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
from applicake.applications.proteomics.openbis.generator import GuseGenerator
from applicake.applications.os.echo import Echo
from applicake.applications.commons.collector import GuseCollector
from applicake.applications.proteomics.searchengine.xtandem import Xtandem
from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mgf

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
TEMPLATE = template.tpl
DATASET_CODE = 20120320164249179-361885,
MZXML = /Users/quandtan/Downloads/proteomics_test/B10-01219.mzXML

DBASE = /Users/quandtan/Downloads/proteomics_test/ex_sp_9606_mimic.fasta
FRAGMASSERR = 0.4
FRAGMASSUNIT = Da
PRECMASSERR = 15
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
THREADS = 4

""" % cwd)       

@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    sys.argv = ['IGNORED', '-i', input_file_name, '--GENERATORS', 'generate.ini' ,'-l','CRITICAL']
    runner = IniFileRunner()
    application = GuseGenerator()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code) 
    
@transform(generator, regex("generate.ini_"), "xtandemout.ini_")
def tandem(input_file_name, output_file_name):
    sys.argv = ['IGNORED', '-i', input_file_name, '-o', output_file_name, 
                '--TEMPLATE', 'xtandem.tpl',
                '--PREFIX', '~/Downloads/proteomics_test/tandem-osx-intel-11-12-01-1/bin/tandem','-l','DEBUG']
    runner = WrapperRunner()
    wrapper = Xtandem()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("echo failed [%s]" % exit_code) 
    
def mzxml2mgf():
    args = 'bla.py --BASEDIR . --STORAGE file --TEMPLATE template.ini --PREFIX FileConverter --MZXML /Users/quandtan/Downloads/proteomics_test/B10-01219.mzXML --MGF B10-01219.mgf' # /Applications/OpenMS-1.9.0/TOPP/
    sys.argv = args.split(' ')
    runner = WrapperRunner()
    application = Mzxml2Mgf()
    exit_code = runner(sys.argv,application)
    print exit_code
    if exit_code != 0:
        raise Exception("mzxml2mzml failed with exit code [%s]" % exit_code)    
       
    
@transform(generator, regex("generate.ini_"), "omssaout.ini_")
@follows(mzxml2mgf)
def omssa(input_file_name, output_file_name):
    sys.argv = ['IGNORED', '-i', input_file_name, '-o', output_file_name, 
                '--TEMPLATE', 'omssa.tpl',
                '--PREFIX', '~/Downloads/proteomics_test/omssa-2.1.9.macos/omssacl','-l','DEBUG']
    runner = WrapperRunner()
    wrapper = Xtandem()
    exit_code = runner(sys.argv, wrapper)
    if exit_code != 0:
        raise Exception("echo failed [%s]" % exit_code)       
    
@merge(omssa, "output.ini")
def collector(notused_input_file_names, output_file_name):
    sys.argv = ['IGNORED', '--COLLECTORS', 'omssaout.ini', '-o', output_file_name,'-s','file']
    runner = CollectorRunner()
    application = GuseCollector()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("collector failed [%s]" % exit_code)    

pipeline_run([collector])


#pipeline_printout_graph ('flowchart.png','png',[collector],no_key_legend = False) #svg
