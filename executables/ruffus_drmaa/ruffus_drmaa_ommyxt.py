#!/usr/bin/env python
'''
Created on Aug 15, 2012

@author: loblum
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
STORAGE = memory_all

DATASET_DIR = /cluster/scratch/malars/datasets
DATASET_CODE = 20110721073234274-201170, 20110721054532782-201128, 20110721034730308-201103
DBASE = /cluster/scratch/malars/biodb/ex_sp/current/decoy/ex_sp_9606.fasta

DECOY_STRING = DECOY_ 
FRAGMASSERR = 0.4
FRAGMASSUNIT = Da
PRECMASSERR = 15,25
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
ENZYME = Trypsin
STATIC_MODS = Carbamidomethyl (C)
VARIABLE_MODS = Phospho (STY)
THREADS = 4
XTANDEM_SCORE = k-score
IPROPHET_ARGS = MINPROB=0
FDR=0.01
SPACE = LOBLUM
PROJECT = TEST
DROPBOX = /cluster/scratch/malars/drop-box_prot_ident
WORKFLOW= ruffus_drmaa_ommyxt
COMMENT = ruffus_drmaa_ommyxt tinasset
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

@transform(myrimatch, regex("myrimatch.ini_"), "myriattr.ini_")
def myriaddr(input_file_name, output_file_name):
    submitter.run('run_addSID2pepxml.py', ['-i',  input_file_name,'-o', output_file_name],lsfargs)
    
@transform(myriaddr, regex("myriattr.ini_"), "myrirefresh.ini_")
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


############################# TAIL: PARAMGENERATE ##################################   


@merge(interprophetengines, "collector.ini")
def collector(notused_input_file_names, output_file_name):
    submitter.run('run_guse_collector.py',['--COLLECTORS', 'interprophetengines.ini', '-o',output_file_name],lsfargs) 

@follows(collector)
@split("collector.ini", "paramgenerate.ini_*")
def paramgenerator(input_file_name, notused_output_file_names):
    submitter.run('run_parameter_generator.py',['-i', input_file_name, '--GENERATORS','paramgenerate.ini','-s','file'],lsfargs)

@transform(paramgenerator, regex("paramgenerate.ini_"), "interprophet.ini_")
def interprophet(input_file_name, output_file_name):
    submitter.run('run_iprophet.py',['-i', input_file_name, '-o',output_file_name],lsfargs)

@transform(interprophet, regex("interprophet.ini_"), "pepxml2csv.ini_")
def pepxml2csv(input_file_name, output_file_name):
    submitter.run('run_pep2csv.py',['-i', input_file_name, '-o',output_file_name],lsfargs)   
    
@transform(pepxml2csv, regex("pepxml2csv.ini_"), "fdr2probability.ini_")
def fdr2probability(input_file_name, output_file_name):
    submitter.run('run_fdr2prob.py',['-i', input_file_name, '-o',output_file_name],lsfargs)           

@transform(fdr2probability, regex("fdr2probability.ini_"), "proteinprophet.ini_") 
def proteinprophet(input_file_name, output_file_name):
    submitter.run('run_pprophet.py',['-i', input_file_name, '-o',output_file_name],lsfargs)   

@transform(proteinprophet, regex("proteinprophet.ini_"), "protxml2spectralcount.ini_") 
def protxml2spectralcount(input_file_name, output_file_name):
    submitter.run('run_protxml2spc.py',['-i', input_file_name, '-o',output_file_name],lsfargs)   

@transform(protxml2spectralcount, regex("protxml2spectralcount.ini_"), "protxml2modifications.ini_")
def protxml2modifications(input_file_name, output_file_name):
    submitter.run('run_protxml2mod.py',['-i', input_file_name, '-o',output_file_name],lsfargs)       

@transform(protxml2modifications, regex("protxml2modifications.ini_"), "protxml2openbis.ini_")
def protxml2openbis(input_file_name, output_file_name):
    submitter.run('run_protxml2openbis.py',['-i', input_file_name, '-o',output_file_name],lsfargs)     

@transform(protxml2openbis, regex("protxml2openbis.ini_"),"copy2dropbox.ini_")
def copy2dropbox(input_file_name, output_file_name):
    submitter.run('run_copy2identdropbox.py',['-i', input_file_name, '-o',output_file_name],lsfargs)         
    
    
        
### MAIN ###
lsfargs = '-q vip.1h -R lustre' 
submitter = DrmaaSubmitter()
pipeline_run([copy2dropbox], multiprocess=12)

#pipeline_printout_graph ('misc/ruffus_drmaa_ommyxt.png','png',[copy2dropbox],no_key_legend = True) #svg