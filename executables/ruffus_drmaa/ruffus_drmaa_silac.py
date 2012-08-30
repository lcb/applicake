#!/usr/bin/env python
'''
Created on Aug 30, 2012

@author: quandtan
'''
import sys
import subprocess
from ruffus import *
from applicake.utils.drmaautils import DrmaaSubmitter

def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
        subprocess.call("rm *ini* *.err *.out",shell=True)    
        with open("input.ini", 'w+') as f:
            f.write("""BASEDIR = /cluster/scratch/malars/workflows
LOG_LEVEL = DEBUG
STORAGE = file

DATASET_DIR = /cluster/scratch/malars/datasets
DATASET_CODE = 20111212003510002-282406,20111212212548508-282587
DBASE = /cluster/scratch/malars/biodb/ex_sp/current/decoy/ex_sp_9606.fasta

DECOY_STRING = DECOY_ 
FRAGMASSERR = 0.4
FRAGMASSUNIT = Da
PRECMASSERR = 15,25
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
ENZYME = Trypsin
STATIC_MODS = Carbamidomethyl (C),13C(6)15(N)(2) (K),13C(6)15(N)(4) (R)
VARIABLE_MODS =
THREADS = 4
XTANDEM_SCORE = k-score
IPROPHET_ARGS = MINPROB=0
FDR=0.01
SPACE = QUANDTAN
PROJECT = TEST
DROPBOX = /cluster/scratch/malars/drop-box_prot_ident
WORKFLOW= ruffus_drmaa_ommyxt
COMMENT = yancheng silac
""")
    else:
        print 'Continuing'
        

@follows(setup)
@split("input.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    submitter.run('run_guse_generator.py',['-i', input_file_name, '--GENERATORS', 'generate.ini'],lsfargs)
       
@transform(generator, regex("generate.ini_"), "dss.ini_")
@jobs_limit(1)
def dss(input_file_name, output_file_name):   
    submitter.run('run_dss.py', ['-i',  input_file_name,'-o', output_file_name,'--PREFIX', 'getmsdata'],lsfargs)


######################### TANDEM #########################################

        
@transform(dss, regex("dss.ini_"), "xtandem.ini_")
def tandem(input_file_name, output_file_name):
   submitter.run('run_xtandem.py', ['-i',  input_file_name,'-o', output_file_name,'--PREFIX', 'tandem.exe'],lsfargs)

@transform(tandem, regex("xtandem.ini_"), "xtandem2xml.ini_")
def tandem2xml(input_file_name, output_file_name):
    submitter.run('run_tandem2xml.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)  

@transform(tandem2xml, regex("xtandem2xml.ini_"), "tandeminteract.ini_")
def tandeminteract(input_file_name, output_file_name,):
     submitter.run('run_interactparser.py', ['-i',  input_file_name,'-o', output_file_name,'-n','tandeminteract'],lsfargs)

@transform(tandeminteract, regex("tandeminteract.ini_"), "tandemrefresh.ini_")
def tandemrefresh(input_file_name, output_file_name):
   submitter.run('run_refreshparser.py', ['-i',  input_file_name,'-o', output_file_name,'-n','tandemrefresh'],lsfargs)

@transform(tandemrefresh, regex("tandemrefresh.ini_"), "tandempeppro.ini_")
def tandemPepPro(input_file_name, output_file_name):
    submitter.run('run_peptideprophet.py', ['-i',  input_file_name,'-o', output_file_name,'-n','tandempeppro'],lsfargs)


########################### MYRI #######################################


@transform(dss, regex("dss.ini_"), "myrimatch.ini_")
def myrimatch(input_file_name, output_file_name):
    submitter.run('run_myrimatch.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)

@transform(myrimatch, regex("myrimatch.ini_"), "myrirefresh.ini_")
def myrirefresh(input_file_name, output_file_name):
     submitter.run('run_refreshparser.py', ['-i',  input_file_name,'-o', output_file_name,'-n','myrirefresh'],lsfargs)

@transform(myrirefresh, regex("myrirefresh.ini_"), "myriinteract.ini_")
def myriinteract(input_file_name, output_file_name,):
    submitter.run('run_interactparser.py', ['-i',  input_file_name,'-o', output_file_name,'-n','myriinteract'],lsfargs)

@transform(myriinteract, regex("myriinteract.ini_"), "myrirefresh2.ini_")
def myrirefresh2(input_file_name, output_file_name):
    submitter.run('run_refreshparser.py', ['-i',  input_file_name,'-o', output_file_name,'-n','myrirefresh2'],lsfargs)

@transform(myrirefresh2, regex("myrirefresh2.ini_"), "myripeppro.ini_")
def myriPepPro(input_file_name, output_file_name):
    submitter.run('run_peptideprophet.py', ['-i',  input_file_name,'-o', output_file_name,'-n','myripeppro'],lsfargs)

    
########################### OMSSA ########################################


@transform(dss, regex("dss.ini_"), "msconvert.ini_")
def msconvert(input_file_name, output_file_name):
    submitter.run('run_mzxml2mgf.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)
    
@transform(msconvert, regex("msconvert.ini_"), "omssa.ini_")
def omssa(input_file_name, output_file_name):
    submitter.run('run_omssa.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)
    
@transform(omssa, regex("omssa.ini_"), "omssainteract.ini_")
def omssainteract(input_file_name, output_file_name):
    submitter.run('run_interactparser.py', ['-i',  input_file_name,'-o', output_file_name,'-n','omssainteract'],lsfargs)   

@transform(omssainteract, regex("omssainteract.ini_"), "omssarefresh.ini_")
def omssarefresh(input_file_name, output_file_name):
    submitter.run('run_refreshparser.py', ['-i',  input_file_name,'-o', output_file_name,'-n','omssarefresh'],lsfargs)

@transform(omssarefresh, regex("omssarefresh.ini_"), "omssapeppro.ini_")
def omssaPepPro(input_file_name, output_file_name):
    submitter.run('run_peptideprophet.py', ['-i',  input_file_name,'-o', output_file_name,'-n','omssapeppro'],lsfargs)


############################# MERGE SEARCH ENGINE RESULTS ################################## 


@collate([omssaPepPro,tandemPepPro,myriPepPro],regex(r".*_(.+)$"),  r'mergeengines.ini_\1')
def mergeEngines(input_file_names, output_file_name):
    args = []
    for f in input_file_names:
        args.append('--COLLECTORS')
        args.append(f)
    args.append('-o')
    args.append(output_file_name)
    submitter.run('run_simple_collector.py', args ,lsfargs)
    
@transform(mergeEngines, regex("mergeengines.ini_"), "unifyengines.ini_")
def unifyEngines(input_file_name, output_file_name):
    submitter.run('run_unify.py', ['-i', input_file_name, '-o',output_file_name,'--UNIFIER_REDUCE'] ,lsfargs)

@transform(unifyEngines, regex("unifyengines.ini_"), "interprophetengines.ini_")
def interprophetengines(input_file_name, output_file_name):
    submitter.run('run_iprophet.py',['-i', input_file_name, '-o',output_file_name],lsfargs)

@transform(interprophetengines, regex("interprophetengines.ini_"), "pepxml2csv.ini_")
def pepxml2csv(input_file_name, output_file_name):
    submitter.run('run_pep2csv.py',['-i', input_file_name, '-o',output_file_name],lsfargs)        
    
@transform(pepxml2csv, regex("pepxml2csv.ini_"), "fdr2probability.ini_")
def fdr2probability(input_file_name, output_file_name):
    submitter.run('run_fdr2prob.py',['-i', input_file_name, '-o',output_file_name],lsfargs)      

@transform(fdr2probability, regex("fdr2probability.ini_"), "proteinprophet.ini_") 
def proteinprophet(input_file_name, output_file_name):
    submitter.run('run_pprophet.py',['-i', input_file_name, '-o',output_file_name],lsfargs) 

############################# SILAC ##################################
    
    

@transform(dss,regex('dss.ini_'),'mzxml2mzml.ini_')
def mzxml2mzml(input_file_name, output_file_name):
    submitter.run('run_mzxml2mzml.py',['-i', input_file_name, '-o',output_file_name],lsfargs)
    
@transform(mzxml2mzml,regex('mzxml2mzml.ini_'),'mzxml2mzml.ini_')
def silacanalyzer(input_file_name, output_file_name):
    submitter.run('run_silacanalyzer.py',['-i', input_file_name, '-o',output_file_name],lsfargs)        
    
@transform(interprophetengines,regex('interprophetengines.ini_'),'pepxml2idxml.ini_')
def pepxml2idxml(input_file_name, output_file_name):
    submitter.run('run_pepxml2idxml.py',['-i', input_file_name, '-o',output_file_name],lsfargs)

@collate([silacanalyzer,pepxml2idxml],regex(r".*_(.+)$"),  r'idmapper.ini_\1')    
def idmapper(input_file_names, output_file_name):
    submitter.run('run_idmapper.py',['-i', input_file_names[0],'-i', input_file_names[1], '-o',output_file_name],lsfargs)

@transform(proteinprophet,regex('proteinprophet.ini_'),'prot2idxml.ini_')
def protxml2idxml(input_file_name, output_file_name):
    submitter.run('run_protxml2idxml.py',['-i', input_file_name, '-o',output_file_name],lsfargs)
    
        
### MAIN ###
lsfargs = '-q vip.1h -R lustre' 
submitter = DrmaaSubmitter()
pipeline_run([idmapper], multiprocess=12)




#@transform(interprophet,regex('interprophet.ini'),'pepxml2idxml.ini')
#def pepxml2idxml(input_file_name, output_file_name):
#    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
#    runner = WrapperRunner()
#    application = PepXml2IdXml()
#    exit_code = runner(sys.argv, application)
#    if exit_code != 0:
#        raise Exception("[%s] failed [%s]" % ('pepxml2idxml',exit_code)) 
#
#@transform(pepxml2idxml,regex('pepxml2idxml.ini'),'peptideindexer.ini')
#def peptideindexer(input_file_name, output_file_name):
#    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
#    runner = WrapperRunner()
#    application = PeptideIndexer()
#    exit_code = runner(sys.argv, application)
#    if exit_code != 0:
#        raise Exception("[%s] failed [%s]" % ('peptideindexer',exit_code))
#
#@transform(peptideindexer,regex('peptideindexer.ini'),'fdr.ini')
#def fdr(input_file_name, output_file_name):
#    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
#    runner = WrapperRunner()
#    application = FalseDiscoveryRate()
#    exit_code = runner(sys.argv, application)
#    if exit_code != 0:
#        raise Exception("[%s] failed [%s]" % ('fdr',exit_code)) 
#    
#@transform(fdr,regex('fdr.ini'),'idfilter.ini')
#def idfilter(input_file_name, output_file_name):
#    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
#    runner = WrapperRunner()
#    application = IdFilter()
#    exit_code = runner(sys.argv, application)
#    if exit_code != 0:
#        raise Exception("[%s] failed [%s]" % ('idfilter',exit_code)) 
#    
#@transform(idfilter,regex('idfilter.ini'),'mzxml2mzml.ini')
#def mzxml2mzml(input_file_name, output_file_name):
#    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
#    runner = WrapperRunner()
#    application = MzXml2MzMl()
#    exit_code = runner(sys.argv, application)
#    if exit_code != 0:
#        raise Exception("[%s] failed [%s]" % ('mzxml2mzml',exit_code)) 
#
#@transform(mzxml2mzml,regex('mzxml2mzml.ini'),'peakpickerhighres.ini')
#def peakpickerhighres(input_file_name, output_file_name):
#    sys.argv = ['', '-i', input_file_name, '-o', output_file_name,'--SIGNAL_TO_NOISE','1']
#    runner = WrapperRunner()
#    application = PeakPickerHighRes()
#    exit_code = runner(sys.argv, application)
#    if exit_code != 0:
#        raise Exception("[%s] failed [%s]" % ('peakpickerhighres',exit_code)) 
#         
#@transform(peakpickerhighres,regex('peakpickerhighres.ini'),'featurefindercentroided.ini')
#def featurefindercentroided(input_file_name, output_file_name):
#    sys.argv = ['', '-i', input_file_name, '-o', output_file_name]
#    runner = WrapperRunner()
##    application = FeatureFinderCentroided()
#    application = OrbiLessStrict()
#    exit_code = runner(sys.argv, application)
#    if exit_code != 0:
#        raise Exception("[%s] failed [%s]" % ('featurefindercentroided',exit_code)) 
#         
