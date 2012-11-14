#!/usr/bin/env python
'''
Created on Nov 14, 2012

@author: quandtan
'''

import sys
import os
import subprocess
from ruffus import *
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.framework.runner import ApplicationRunner, WrapperRunner,\
    IniFileRunner
from applicake.applications.commons.generator import GenericGenerator
from applicake.applications.biodb.fasta2inspect import Fasta2Inspect
from applicake.applications.biodb.fasta2omssa import Fasta2Omssa

    
#helper function
def wrap(applic,  input_file_name, output_file_name,opts=None):
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
    cwd = '.'
    os.chdir(cwd)
    print os.getcwd()    
#    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
    print 'Starting from scratch by creating new input.ini'
    subprocess.call("rm *.ini* *.err *.out",shell=True)    
    with open("input.ini", 'w+') as f:
        f.write("""
BASEDIR = /home/quandtan/tmp
LOG_LEVEL = DEBUG
STORAGE = file
WORKFLOW = biodb_fasta2bin
FASTA = /home/quandtan/tmp/20121114_010943_465934/MimicPostprocess/9606.fasta, /home/quandtan/tmp/20121114_010943_465934/MimicPostprocess/10090.fasta, /home/quandtan/tmp/20121114_010943_465934/MimicPostprocess/562.fasta, /home/quandtan/tmp/20121114_010943_465934/MimicPostprocess/7227.fasta, /home/quandtan/tmp/20121114_010943_465934/MimicPostprocess/10116.fasta, /home/quandtan/tmp/20121114_010943_465934/MimicPostprocess/YEAST.fasta, /home/quandtan/tmp/20121114_010943_465934/MimicPostprocess/ECOLI.fasta 
""")
#/cluster/scratch_xl/shareholder/imsb_ra/workflows
#    else:
#        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    

@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    argv = ['', '-i', input_file_name, '--GENERATORS', 'generate.ini','-o','generator.ini','-l','DEBUG']
    runner = IniFileRunner()
    application = GenericGenerator()
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("generator failed [%s]" % exit_code)     
    
@transform(generator, regex("generate.ini_"), "fasta2inspect.ini_")
def fasta2inspect(input_file_name, output_file_name):
    wrap(Fasta2Inspect,input_file_name, output_file_name,['--PREFIX','python2.7 /usr/local/apps/inspect/PrepDB.py'])

@transform(generator, regex("generate.ini_"), "fasta2omssa.ini_")
def fasta2omssa(input_file_name, output_file_name):
    wrap(Fasta2Omssa,input_file_name, output_file_name,['--PREFIX','formatdb'])



pipeline_run([fasta2inspect,fasta2omssa], multiprocess=5)