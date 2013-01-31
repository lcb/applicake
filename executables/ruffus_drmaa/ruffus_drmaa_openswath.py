#!/usr/bin/env python
'''
Created on Aug 15, 2012

@author: loblum
'''
import sys
import subprocess
import tempfile
from ruffus import *
#from applicake.utils.drmaautils import DrmaaSubmitter

def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart': 
        print 'Restarting by creating new input.ini'  
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
LOG_LEVEL = INFO
STORAGE = memory_all
THREADS = 32
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

IRTTRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_DIA_iRT.TraML"

DATASET_CODE = 20120716161635740-638989 , 20120718153522983-639951,20120718155728388-639953,20120713111747469-637629,20120712220845703-637087,20120712223851302-637152,20120712224941366-637167,20120712230941150-637209,20120713110540978-637614,20120712234046060-637316,20120712234054529-637317,20120712234103658-637318,20120712234111320-637319,20120713110549117-637615,20120713001146738-637333,20120713002246440-637341,20120713002252530-637342,20120713004247476-637349,20120713005347029-637351,20120713110650516-637617,20120713110640147-637616,20120713013348351-637369,20120713013354501-637370,20120713110745791-637620,20120713110752716-637621,20120713110800366-637622,20120713022439616-637404,20120713110841965-637623,20120713024507292-637417,20120713030508028-637422

TRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_AQUASky_ShotgunLibrary_3t_345_sh.TraML"


EXTRACTION_WINDOW = 0.05
RT_EXTRACTION_WINDOW = 600

MIN_UPPER_EDGE_DIST = 1

MIN_RSQ = 0.95
MIN_COVERAGE = 0.6

MPR_NUM_XVAL = 5

SPACE = LOBLUM
PROJECT = TEST
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/openbis_dropbox

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
    submitter.run('run_denoiser.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs) 

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
   
@transform(mprophet, regex("mprophet.ini_"), "tsvtoxml.ini_")
def tsvtoxml(input_file_name, output_file_name):   
    submitter.run('run_rewritexmltotsv.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)
       
@transform(tsvtoxml, regex("tsvtoxml.ini_"), "gzipxml.ini_")
def gzipxml(input_file_name, output_file_name):   
    submitter.run('run_gzipxml.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)

@merge(gzipxml,"gzipxml.ini_", "runbash.ini")
def runbash(inputfiles,outputfile):
    subprocess.check_call("./makelinks.sh %s" % inputfiles)
    subprocess.check_call("./after_AQUA_run.sh" % inputfiles)
    subprocess.check_call("./after_AQUA_run2.sh" % inputfiles)
        
### MAIN ###

lsfargs = '-q vip.1h -R lustre'
lsf16args = '-n 16 -q vip.1h -R lustre'
#submitter = DrmaaSubmitter()

pipeline_run([runbash], multiprocess=12)
#pipeline_printout_graph('/Users/lorenz/Desktop/flowchart.png','png',[gzipxml]) #svg

