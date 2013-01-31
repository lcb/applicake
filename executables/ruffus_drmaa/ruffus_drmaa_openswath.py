#!/usr/bin/env python
'''
Created on Aug 15, 2012

@author: loblum

'''
import sys
import subprocess
import tempfile
from ruffus import *
from applicake.utils.drmaautils import DrmaaSubmitter

def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart': 
        print 'Restarting by creating new input.ini'  
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
LOG_LEVEL = INFO
STORAGE = memory_all
THREADS = 16
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

IRTTRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_DIA_iRT.TraML"

#human yeast water
DATASET_CODE = 20121213183933423-752451, 20120713070736291-637539, 20120712220845703-637087

TRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_AQUASky_ShotgunLibrary_3t_345_sh.TraML"


EXTRACTION_WINDOW = 0.05
RT_EXTRACTION_WINDOW = 600
WINDOW_UNIT = Thomson

MPR_USE_LDA = False
MIN_UPPER_EDGE_DIST = 1

MIN_RSQ = 0.95
MIN_COVERAGE = 0.6

MPR_NUM_XVAL = 5

WIDTH = 20
RTWIDTH = 9
""")
    else:
        print 'Continuing'
        

@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    submitter.run('run_guse_generator.py',['-i', input_file_name, '--GENERATORS', 'generate.ini'],lsfargs)
       
@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):   
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata',dir='.') 
    submitter.run('run_dss.py', ['-i',  input_file_name,'-o', output_file_name,'--PREFIX', 'getmsdata','--RESULT_FILE',tfile],lsfargs)

@transform(dss, regex("dss.ini_"), "split.ini_")
def split(input_file_name, output_file_name):   
    submitter.run('run_splitwindows.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '16'],lsf16args)

@transform(split, regex("split.ini_*"), "denoised.ini_")
def denoised(input_file_name, output_file_name):
    submitter.run('run_denoiser.py', ['-i',  input_file_name,'-o', output_file_name],lsf36args) 

@transform(denoised, regex("denoised.ini_"), "rtchromextract.ini_")
def rtchromextract(input_file_name, output_file_name):   
    submitter.run('run_irtchromextract.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '16'],lsf16args)
      
@transform(rtchromextract, regex("rtchromextract.ini_"), "rtnorm.ini_")
def rtnorm(input_file_name, output_file_name):   
    submitter.run('run_rtnorm.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '16'],lsf16args)
     
@transform(rtnorm, regex("rtnorm.ini_"), "chromextract.ini_")
def chromextract(input_file_name, output_file_name):   
    submitter.run('run_chromextract.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '16'],lsf16args)
     
@transform(chromextract, regex("chromextract.ini_"), "analyzer.ini_")
def analyzer(input_file_name, output_file_name):   
    submitter.run('run_swathanalyzer.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '16'],lsf16args)
 
@transform(analyzer, regex("analyzer.ini_"), "xmltotsv.ini_")
def xmltotsv(input_file_name, output_file_name):   
    submitter.run('run_xtmltotsv.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)
 
@transform(xmltotsv, regex("xmltotsv.ini_"), "mprophet.ini_")
def mprophet(input_file_name, output_file_name):   
    submitter.run('run_swathmprophet.py', ['-i',  input_file_name,'-o', output_file_name,'--MPROPHET_BINDIR','/cluster/apps/openms/openswath-testing/mapdiv/scripts/mProphet/'],lsfargs)
   
#@transform(mprophet, regex("mprophet.ini_"), "tsvtoxml.ini_")
#def tsvtoxml(input_file_name, output_file_name):   
#    submitter.run('run_rewritexmltotsv.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)
       
#@transform(tsvtoxml, regex("tsvtoxml.ini_"), "gzipxml.ini_")
#def gzipxml(input_file_name, output_file_name):   
#    submitter.run('run_gzipxml.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)

@merge(mprophet,"mprophet.ini_", "runbash.ini")
def runbash(inputfiles,outputfile):
    subprocess.check_call("makelinks.sh %s" % inputfiles)
    subprocess.check_call("after_AQUA_run.sh")
    subprocess.check_call("after_AQUA_run2.sh")
        
### MAIN ###

lsfargs = '-q vip.1h -R lustre'
lsf36args = '-q vip.36h -R lustre'
lsf16args = '-n 16 -q vip.1h -R lustre'
submitter = DrmaaSubmitter()

pipeline_run([runbash], multiprocess=30)
#pipeline_printout_graph('/Users/lorenz/Desktop/flowchart.png','png',[gzipxml]) #svg