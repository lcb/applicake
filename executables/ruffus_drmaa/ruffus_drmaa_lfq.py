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
            f.write("""
BASEDIR = /cluster/scratch_xl/shareholder/imsb_ra/workflows
DATASET_DIR = /cluster/scratch_xl/shareholder/imsb_ra/datasets
LOG_LEVEL = DEBUG
STORAGE = memory_all
WORKFLOW = newLFQ
COMMENT = newLFQ

PEPXML_FDR = 0.01
SEEDS = NO
MAPALIGNER = YES
USERNAME = loblum
SPACE = LOBLUM
PROJECT = TEST

DATASET_CODE = E286812
MSFILES = 20110722014852343-201543, 20110722033454238-201588

FeatureFinder.type = centroided
FeatureFinder.bins = 10
FeatureFinder.mass_trace__mz_tolerance = 0.01
FeatureFinder.mass_trace__min_spectra = 8
FeatureFinder.mass_trace__max_missing = 2
FeatureFinder.mass_trace__slope_bound = 1
FeatureFinder.isotopic_pattern__charge_low = 2
FeatureFinder.isotopic_pattern__charge_high = 6
FeatureFinder.isotopic_pattern__mz_tolerance = 0.01
FeatureFinder.isotopic_pattern__intensity_percentage = 10
FeatureFinder.isotopic_pattern__intensity_percentage_optional = 0.1
FeatureFinder.isotopic_pattern__optional_fit_improvement = 2
FeatureFinder.isotopic_pattern__mass_window_width = 25
FeatureFinder.seed__min_score = 0.5
FeatureFinder.fit__epsilon_abs = 0.0001
FeatureFinder.fit__epsilon_rel = 0.0001
FeatureFinder.fit__max_iterations = 500
FeatureFinder.feature__min_score = 0.5
FeatureFinder.feature__min_isotope_fit = 0.6
FeatureFinder.feature__min_trace_score = 0.4
FeatureFinder.feature__min_rt_span = 0.333
FeatureFinder.feature__max_rt_span = 2.5
FeatureFinder.feature__rt_shape = symmetric
FeatureFinder.feature__max_intersection = 0.35
FeatureFinder.feature__reported_mz = monoisotopic
FeatureFinder.user_seed__rt_tolerance = 30
FeatureFinder.user_seed__mz_tolerance = 0.1
FeatureFinder.user_seed__min_score = 0.5
FeatureFinder.debug__pseudo_rt_shift = 500
FeatureLinker.type = unlabeled_qt
FeatureLinker.keep_subelements = false
FeatureLinker.use_identifications = true
FeatureLinker.ignore_charge = false
FeatureLinker.distance_RT__max_difference = 60
FeatureLinker.distance_RT__exponent = 1
FeatureLinker.distance_RT__weight = 1
FeatureLinker.distance_MZ__max_difference = 0.02
FeatureLinker.distance_MZ__unit = Da
FeatureLinker.distance_MZ__exponent = 2
FeatureLinker.distance_MZ__weight = 1
FeatureLinker.distance_intensity__exponent = 1
FeatureLinker.distance_intensity__weight = 0
IDMapper.rt_tolerance = 5
IDMapper.mz_tolerance = 40
IDMapper.mz_measure = ppm
IDMapper.mz_reference = peptide
IDMapper.ignore_charge = false
IDMapper.use_centroid_rt = false
IDMapper.use_centroid_mz = true
IDMapper.use_subelements = false
MapAligner.type = identification
MapAligner.invert = false
MapAligner.reference__index = 0
MapAligner.model__type = b_spline
MapAligner.model__symmetric_regression = false
MapAligner.model__num_breakpoints = 5
MapAligner.model__interpolation_type = linear
MapAligner.algorithm__peptide_score_threshold = 0
MapAligner.algorithm__min_run_occur = 2
MapAligner.algorithm__max_rt_shift = 0.5
MapAligner.algorithm__use_unassigned_peptides = true
MapAligner.algorithm__use_feature_rt = false
PeakPicker.type = high_res
PeakPicker.signal_to_noise = 0
PeakPicker.ms1_only = true
PeakPicker.estimate_peak_width = false
ProteinQuantifier.top = 3
ProteinQuantifier.average = median
ProteinQuantifier.include_all = true
ProteinQuantifier.filter_charge = false
ProteinQuantifier.consensus__normalize = false
ProteinQuantifier.consensus__fix_peptides = false
ProteinQuantifier.format__separator = ,
ProteinQuantifier.format__quoting = double
ProteinQuantifier.format__replacement = _
SeedListGenerator.use_peptide_mass = true
""")
    else:
        print 'Continuing'
        

@follows(setup)
def getexperiment():
    submitter.run('run_dss.py', ['-i',  'input.ini','-o', 'getexperiment.ini','--PREFIX', 'getexperiment','--DSSKEYS','EXPERIMENTFILES'],lsfargs)

@follows(getexperiment)
def processexperiment():
    submitter.run('run_processexperiment.py', ['-i',  'getexperiment.ini','-o', 'processexperiment.ini'],lsfargs)

@follows(processexperiment)    
@split("processexperiment.ini", "generate.ini_*")
def generator(input_file_name, notused_output_file_names):
    submitter.run('run_guse_generator.py',['-i', input_file_name, '--GENERATORS', 'generate.ini'],lsfargs)
       
@transform(generator, regex("generate.ini_"), "dss.ini_")
def dss(input_file_name, output_file_name):   
    submitter.run('run_dss.py', ['-i',  input_file_name,'-o', output_file_name,'--PREFIX', 'getmsdata'],lsfargs)

        
### MAIN ###
lsfargs = '-q vip.1h -R lustre' 
submitter = DrmaaSubmitter()
pipeline_run([dss], multiprocess=12)