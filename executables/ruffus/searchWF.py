#!/usr/bin/env python
import os
import shutil
import sys
import subprocess
from ruffus import *
from multiprocessing import freeze_support


basepath = os.path.dirname(__file__) + '/../../'

def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'cont':
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    else:
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.log", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""
LOG_LEVEL = DEBUG
COMMENT = WFTEST - newUPS TPP


FDR_CUTOFF = 0.01
FDR_TYPE = iprophet-pepFDR
FRAGMASSERR = 0.5
FRAGMASSUNIT = Da
PRECMASSERR = 15
PRECMASSUNIT = ppm
MISSEDCLEAVAGE = 0
ENZYME = Nonspecific
STATIC_MODS =
VARIABLE_MODS = Oxidation (M)

DECOY_STRING = DECOY_
IPROPHET_ARGS = MINPROB=0

MZXML=D:/projects/p1958/data/datafiles/mzXML/C1R1_Monash_RS_20141103_B2702_IDA_c.mzXML,D:/projects/p1958/data/datafiles/mzXML/C1R1_Monash_RS_20141103_B2702_IDA_c.mzXML

DBASE=D:/projects/p1958/data/databases/CNCL_05640_2015_09_DECOY.fasta

COMET_DIR=D:/projects/p1958/prog/searchEngines/comet_binaries_2015020
COMET_EXE=comet.2015020.win64.exe
MYRIMATCH_DIR=D:/projects/p1958/prog/searchEngines/myrimatch
MYRIMATCH_EXE=myrimatch.exe

""")


@follows(setup)
@split("input.ini", "split.ini_*")
def split_dataset(infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/split.py',
                           '--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'MZXML'])

###################################################################################

@transform(split_dataset, regex("split.ini_"), "rawmyri.ini_")
def myri(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/searchengines/myrimatch.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--THREADS', '4'])


@transform(myri, regex("rawmyri.ini_"), "myrimatch.ini_")
def peppromyri(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/peptideprophet.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--NAME', 'pepmyri'])

###################################################################################

@transform(split_dataset, regex("split.ini_"), "rawcomet.ini_")
def comet(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/searchengines/comet.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--THREADS', '4'])


@transform(comet, regex("rawcomet.ini_"), "comet.ini_")
def pepprocomet(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/peptideprophet.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--NAME', 'pepcomet'])


############################# MERGE SEARCH ENGINE RESULTS ##################################
#In guse version conditional branching is used which requires collate to be a full collector to work
#thus enginecollate is a collector/generator node in guse and simulated in ruffus with a merge/fake_split
@merge([pepprocomet,peppromyri], "ecollate.ini")
def collateengines(infiles, outfiles):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/enginecollate.py',
                           '--INPUT','biopersdb.ini','--OUTPUT','ecollate.ini','--MERGED', 'mergeengine.ini',
                           '--ENGINES', 'myrimatch',  '--ENGINES', 'comet'])

@split(collateengines,"mergeengine.ini_*")
def fake_split(infile,outfiles):
    pass

@transform(fake_split, regex("mergeengine.ini_"), "engineiprophet.ini_")
def engineiprophet(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/interprophet.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--NAME', 'engineiprophet'])

############################# TAIL: PARAMGENERATE ##################################

@merge(engineiprophet, "mergedatasets.ini")
def merge_datasets(unused_infiles, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/merge.py',
                           '--MERGE', 'engineiprophet.ini', '--MERGED', outfile])

@follows(merge_datasets)
@files("mergedatasets.ini_0", "datasetiprophet.ini")
def datasetiprophet(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/tpp/interprophet.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

if __name__ == '__main__':

    freeze_support() # Optional under circumstances described in docs
    pipeline_run([datasetiprophet])

#pipeline_printout_graph ('flowchart.png','png',[copy2dropbox],no_key_legend = False) #svg
