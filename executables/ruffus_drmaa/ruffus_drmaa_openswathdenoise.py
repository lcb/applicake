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
        print 'Restarting by creating new input.txt'  
        with open("input.txt", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
LOG_LEVEL = INFO
JOB_IDX = oswdenoise
STORAGE = memory_all
THREADS = 16
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets

IRTTRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_DIA_iRT.TraML"

#1 each human yeast water
#DATASET_CODE = 20121213183933423-752451, 20120713070736291-637539, 20120712220845703-637087
#all at once
DATASET_CODE = 20120716161635740-638989, 20120718153522983-639951, 20120718155728388-639953, 20120713111747469-637629, 20120712220845703-637087, 20120712223851302-637152, 20120712224941366-637167, 20120712230941150-637209, 20120713110540978-637614, 20120712234046060-637316, 20120712234054529-637317, 20120712234103658-637318, 20120712234111320-637319, 20120713110549117-637615, 20120713001146738-637333, 20120713002246440-637341, 20120713002252530-637342, 20120713004247476-637349, 20120713005347029-637351, 20120713110650516-637617, 20120713110640147-637616, 20120713013348351-637369, 20120713013354501-637370, 20120713110745791-637620, 20120713110752716-637621, 20120713110800366-637622, 20120713022439616-637404, 20120713110841965-637623, 20120713024507292-637417, 20120713030508028-637422, 20120713111242263-637624, 20120713111741020-637628, 20120713070736291-637539, 20120713073036626-637547, 20120713090238342-637572, 20120713095539236-637589, 20120713111442632-637625, 20120713182147648-637794, 20120713184447812-637812, 20120713144243438-637679, 20120713142943497-637677, 20120713160444831-637702, 20120713162651767-637717, 20120713163945808-637721, 20121219194613788-755063, 20120713184747929-637813, 20120713202051925-637868, 20121219201232691-755198, 20120718173224705-640023, 20120718172925387-640022, 20120718044013373-639706, 20120713202249234-637869, 20121219210824521-755321, 20120713214622656-637920, 20121219213133424-755327, 20120716221443403-639099, 20121219215605944-755352, 20120716191838914-639041, 20120717201504387-639543, 20120718025510695-639653, 20121213183933423-752451, 20121213190633328-752455, 20121213193133517-752459, 20121213212633663-752473, 20121213214333653-752474, 20121213220733795-752475, 20121214001533869-752483, 20121214003133973-752488, 20121214004733839-752491, 20121214025234015-752496, 20121214030434050-752499, 20121214031434002-752500, 20121214044334123-752505, 20121214050334001-752510, 20121214052234179-752511, 20121214064234302-752517, 20121214070334049-752518, 20121214072334328-752523, 20121214084334391-752528, 20121214090334521-752531, 20121214092234441-752532, 20121214105035364-752547, 20121214110134560-752565, 20121214111034549-752590, 20121214125034721-752675, 20121214125934595-752676, 20121214130734606-752677, 20121214144634746-752757, 20121214145434687-752758, 20121214150234788-752768

TRAML = "/cluster/scratch_xl/shareholder/imsb_ra/openswath/tramlpile/hroest_AQUASky_ShotgunLibrary_3t_345_sh.TraML"


EXTRACTION_WINDOW = 0.05
RT_EXTRACTION_WINDOW = -1
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
@split("input.txt", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    submitter.run('run_guse_generator.py',['-i', input_file_name, '--GENERATORS', 'generate.ini'],lsfargs)
       
@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):   
    thandle, tfile = tempfile.mkstemp(suffix='.out', prefix='getmsdata',dir='.') 
    submitter.run('run_dss.py', ['-i',  input_file_name,'-o', output_file_name,'--PREFIX', 'getmsdata','--RESULT_FILE',tfile],lsfargs)

@transform(dss, regex("dss.ini_"), "split.ini_")
def split(input_file_name, output_file_name):   
    submitter.run('run_splitwindows.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '16'],'-n 16 -q vip.1h -R lustre')

@transform(split, regex("split.ini_"), "denoised.ini_")
def denoised(input_file_name, output_file_name):
    submitter.run('run_denoiser.py', ['-i',  input_file_name,'-o', output_file_name],'-q vip.36h -R lustre') 

@transform(denoised, regex("denoised.ini_"), "rtchromextract.ini_")
def rtchromextract(input_file_name, output_file_name):   
    submitter.run('run_irtchromextract.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '1'],'-n 1 -q vip.8h -R lustre -R "rusage[mem=20000]"')
      
@transform(rtchromextract, regex("rtchromextract.ini_"), "rtnorm.ini_")
def rtnorm(input_file_name, output_file_name):   
    submitter.run('run_rtnorm.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '4'],'-n 4 -q vip.1h -R lustre -R "rusage[mem=4096]"')
     
@transform(rtnorm, regex("rtnorm.ini_"), "chromextract.ini_")
def chromextract(input_file_name, output_file_name):   
    submitter.run('run_chromextract.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '1'],'-n 1 -q vip.8h -R lustre -R "rusage[mem=20000]"')
     
@transform(chromextract, regex("chromextract.ini_"), "analyzer.ini_")
def analyzer(input_file_name, output_file_name):   
    submitter.run('run_swathanalyzer.py', ['-i',  input_file_name,'-o', output_file_name,'--THREADS', '4'],'-n 4 -q vip.1h -R lustre -R "rusage[mem=4096]"')
 
@transform(analyzer, regex("analyzer.ini_"), "xmltotsv.ini_")
def xmltotsv(input_file_name, output_file_name):   
    submitter.run('run_xmltotsv.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)
 
@transform(xmltotsv, regex("xmltotsv.ini_"), "mprophet.ini_")
def mprophet(input_file_name, output_file_name):   
    submitter.run('run_swathmprophet.py', ['-i',  input_file_name,'-o', output_file_name,'--MPROPHET_BINDIR','/cluster/apps/openms/openswath-testing/mapdiv/scripts/mProphet/'],lsfargs)

@merge(mprophet,"runbash.ini")
def runbash(inputfiles,outputfile):
    subprocess.call("rm drmaa* getmsdata*", shell=True)    
    subprocess.check_call("makelinks.sh %s" % ' '.join(inputfiles), shell=True)
    subprocess.check_call("after_AQUA_run.sh", shell=True)
    subprocess.check_call("cd rerun_mpr; after_AQUA_run2.sh", shell=True)
    open("runbash.ini", 'w').write('')

### MAIN ###

lsfargs = '-q vip.1h -R lustre'
submitter = DrmaaSubmitter()

pipeline_run([runbash], multiprocess=30)
#pipeline_printout_graph('/Users/lorenz/Desktop/flowchart.png','png',[gzipxml]) #svg