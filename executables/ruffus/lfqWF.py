#!/usr/bin/env python
import os
import sys
import subprocess

from ruffus import *


basepath = os.path.dirname(__file__) + '/../../'


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'cont':
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    else:
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.log", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("""
WORKFLOW = wf
LOG_LEVEL = DEBUG
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows/
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets/
DROPBOX = /cluster/scratch_xl/shareholder/imsb_ra/drop-box_prot_quant
COMMENT = WFTEST - newUPS LFQ

FDR_CUTOFF = 0.01
FDR_TYPE = iprophet-pepFDR
FEATUREFINDER_MASS_TRACE__MZ_TOLERANCE = 0.03
FEATUREFINDER_MASS_TRACE__MIN_SPECTRA = 10
FEATUREFINDER_MASS_TRACE__MAX_MISSING = 1
FEATUREFINDER_MASS_TRACE__SLOPE_BOUND = 0.1
FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_LOW = 1
FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_HIGH = 4
FEATUREFINDER_ISOTOPIC_PATTERN__MZ_TOLERANCE = 0.03
FEATUREFINDER_SEED__MIN_SCORE = 0.8
FEATUREFINDER_FEATURE__MIN_SCORE = 0.7
FEATUREFINDER_FEATURE__MIN_ISOTOPE_FIT = 0.8
FEATUREFINDER_FEATURE__MIN_TRACE_SCORE = 0.5
FEATURELINKER_DISTANCE_RT__MAX_DIFFERENCE = 100
FEATURELINKER_DISTANCE_MZ__MAX_DIFFERENCE = 0.3
FEATURELINKER_DISTANCE_MZ__UNIT = Da
IDMAPPER_RT_TOLERANCE = 5
IDMAPPER_MZ_TOLERANCE = 20
IDMAPPER_MZ_REFERENCE = precursor
IDMAPPER_USE_CENTROID_MZ = false
POSECLUSTERING_MZ_PAIR_MAX_DISTANCE = 0.5
POSECLUSTERING_DISTANCE_MZ_MAX_DIFF = 0.3
POSECLUSTERING_DISTANCE_RT_MAX_DIFF = 100
PEAKPICKER_SIGNAL_TO_NOISE = 1
PEAKPICKER_MS1_ONLY = false
PROTEINQUANTIFIER_TOP = 0
PROTEINQUANTIFIER_AVERAGE = median
PROTEINQUANTIFIER_INCLUDE_ALL = true

SPACE = LOBLUM
PROJECT = JUNK
EXPERIMENT = E1309101552
DATASET_CODE = 20120320163951515-361883,20120320163653755-361882,20120320164249179-361886
""")

@follows(setup)
@files('input.ini', 'getexperiment.ini')
def getexperiment(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/dss.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--EXECUTABLE', 'getexperiment'])


@follows(getexperiment)
@files('getexperiment.ini', 'processexperiment.ini')
def processexperiment(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/processexperiment.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


################################################################################################

@follows(processexperiment)
@split('processexperiment.ini', "split.ini_*")
def split_dataset(infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/split.py',
                           '--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'DATASET_CODE'])


@transform(split_dataset, regex("split.ini_"), "dss.ini_")
def dss(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/openbis/dss.py',
                           '--INPUT', infile, '--OUTPUT', outfile, '--EXECUTABLE', 'getmsdata'])


@transform(dss, regex("dss.ini_"), "ppff.ini_")
def pp_ff(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/lfq/peakpicker_featurefinder.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@merge(pp_ff, "mergedataset.ini_0")
def merge_dataset(unused_infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/merge.py',
                           '--MERGE', 'ppff.ini', '--MERGED', 'mergedataset.ini'])


################################################################################################

@follows(merge_dataset)
@files("mergedataset.ini_0", "mafl.ini")
def ma_fl(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/lfq/mapaligner_featurelinker.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@follows(ma_fl)
@files("mafl.ini", "annot.ini")
def annotxml(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/lfq/annotxmlfromcsv.py',
                           '--INPUT', infile, '--OUTPUT', outfile])
@follows(annotxml)
@files("annot.ini", "cp2drobox.ini")
def cp2dropbox(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/lfq/dropbox.py',
                           '--INPUT', infile, '--OUTPUT', outfile])

################################################################################################
#resourcetests | old set        | lars musser | oldUPS      | carone      | olga        | newset
#part1 pp-ff   | 8h 9Gram 9Gscr | 3.2Gs 4063r | 3.8Gs 5881r | 7.1Gs 2672r | 4.6Gs 2738r | 8h 6000ram 7000scr
#part2 ma-fl   | 36h 8Gr 16Gs   | 5.4Gs 10662r| 833s 2353r  | 2.1Gs 3518r | 2.1Gs 2600r | 36h 5000ram 5000scr   

pipeline_run([cp2dropbox], multiprocess=3)
#pipeline_printout_graph ('flowchart.png','png',[idfilter],no_key_legend = False) #svg
