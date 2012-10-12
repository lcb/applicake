'''
Created on Sep 29, 2012

@author: quandtan
'''

import os
import sys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler

class LibraryCreator(IWrapper):
    '''
    Wrapper for SpectraST in library creation mode.
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'spectrast'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file1 = '%s.splib' % base # result produced by the application
        self._result_file2 = '%s.sptxt' % base # result produced by the application


    def get_suffix(self,info,log):
        """
        add command line arguments specific to the library creation step.
        """
        raise NotImplementedError("get_suffix() is not implemented") 

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        # needs to run as first because of the possible overwriting of key values.
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        # need to make old values accessible if existing
        self._orig_splib = None
        self.orig_sptxt  = None
        if info.has_key(self.SPLIB):
            self._orig_splib = info[self.SPLIB]
        if info.has_key(self.SPTXT):
            self._orig_sptxt = info[self.SPTXT]                
        self._result_file1 = os.path.join(wd,self._result_file1)
        info[self.SPLIB] = self._result_file1
        self._result_file2 = os.path.join(wd,self._result_file2)
        info[self.SPTXT] = self._result_file2
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        log.debug('get template handler')
        th = LibraryCreatorTemplate()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        prefix,info = self.get_prefix(info,log)
        spectrast_log = os.path.join(info[self.WORKDIR],'app.log')
        suffix = self.get_suffix(info, log)
        command = '%s -cF%s -V -L%s %s ' % (prefix,self._template_file,spectrast_log,suffix)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        #args_handler.add_app_args(log, '', '')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        return 0,info

class RawLibrary(LibraryCreator):
    
    def get_suffix(self,info,log):
        if len(info[self.PEPXMLS]) >1:
            log.fatal('found > 1 pepxml files [%s] in [%s].' % (len(info[self.PEPXMLS]),info[self.PEPXMLS]))
            sys.exit(1)              
        root = os.path.splitext(self._result_file1)[0]    
        return '-cP%s -cN%s %s ' % (info[self.PROBABILITY],root,self.PEPXMLS[0])

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(RawLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, self.PROBABILITY, 'Probabilty cutoff value that has to be matched') 
        return args_handler

class NoDecoyLibrary(LibraryCreator):
    
    def get_suffix(self,info,log):
        return "-cf'Protein !~ REV_  &  Protein !~ DECOY_' -cN%s %s" % (self._orig_splib,info[self.SPLIB])

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(NoDecoyLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        return args_handler

#spectrast -cf'Protein !~ REV_  &  Protein !~ DECOY_' -cNdecoy_removed raw.splib >spectrast_decoyremoved.log

class LibraryCreatorTemplate(BasicTemplateHandler):
    """
    Template handler for MyClass.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """
### COMMON OPTIONS ##############################

### GENERAL ###

# Output file name (without the extension)
outputFileName = /destination/directory/myLibrary

### PEPXML ###

# Set the minimum probability for an identification to be imported into library
minimumProbabilityToInclude = 0.9

# Dataset identifier
datasetName = 

### LIBRARY MANIPULATION ###  

# Filtering library by criteria
filterCriteria =

# Use probability table to filter library (and modify probabilities)
useProbTable = 

# Use protein list to filter library
useProteinList = 

# Print MRM transition table
printMRMTable = 

# Combining multiple libraries. Choices are UNION, INTERSECT, SUBTRACT and SUBTRACT_HOMOLOG
combineAction = UNION

# Building libraries. Choices are CONSENSUS, BEST_REPLICATE. If not specified, all library
# entries will be left as is.
buildAction =

# Refresh protein mappings against FASTA file specified
refreshDatabase = 

# Whether to delete entries with unmapped peptide during refreshing
refreshDeleteUnmapped = false

# Whether to delete entries with multimapped peptide during refreshing
refreshDeleteMultimapped = false

### CONSENSUS ###

# The minimum number of replicates for a peptide ion to be included in library
minimumNumReplicates = 1

### QUALITY FILTER ###

# The quality level for removing spectra from the library
qualityLevelRemove = 2

# The quality level for marking spectra in the library
qualityLevelMark = 5

### DECOY ###

# Whether or not to concatenate real and decoy libraries
decoyConcatenate = false

# The (decoy /real) size ratio
decoySizeRatio = 1

### SEMI-EMPIRICAL SPECTRA ###

# Set(s) of allowable modification tokens to generate semi-empirical spectra
allowableModTokens = 

### ADVANCED OPTIONS ############################

### GENERAL ###

# Insert a remark in the comment for each library entry created
remark = 

# Whether or not to re-annotate peaks in library entries even if annotations are already present
annotatePeaks = true

# Whether or not to use binary format for library created
binaryFormat = true

# Write all library spectra as .dta or .mgf files
# (e.g. for sequence-searching them)
writeDtaFiles = false
writeMgfFiles = false

### PEPXML ###
    
# Set the minimum number of amino acids in identification to be included
minimumNumAAToInclude = 6

# Whether to force all N in NXS/T motif to be deamidated (glyco-capture datasets)
setDeamidatedNXST = false

# Whether to add mzXML file to the datasetName (e.g. to distinguish between fractions)
addMzXMLFileToDatabaseName = false

# Set the minimum number of peaks for a spectrum to be included
minimumNumPeaksToInclude = 10

# Set the minimum SEQUEST deltaCn value for a spectrum to be included
minimumDeltaCnToInclude = 0.0

# Absolute noise filter. Remove noise peaks with intensity below this value.
rawSpectraNoiseThreshold = 0.0

# Relative noise filter. Remove noise peaks with intensity below the max intensity divided by this value.
rawSpectraMaxDynamicRange = 100000.0

# Whether or not to centroid peaks. Mostly for Q-TOF spectra in profile mode.
centroidPeaks = false

# Override fragmentation type 
setFragmentation =


### LIBRARY MANIPULATION ###

# Whether or not to plot library spectra.
plotSpectra =
  
### CONSENSUS ###

# Peak quorum, the minimum fraction of replicates containing a peak for that peak to be
# included in the consensus
peakQuorum = 0.6

# Maximum number of peaks used in each replicate in consensus creation
maximumNumPeaksUsed = 300

# Maximum number of peaks kept in the consensus spectra
maximumNumPeaksKept = 150

# Maximum number of replicates used in consensus creation
maximumNumReplicates = 100

# Whether or not to remove dissimilar replicates from consensus building
removeDissimilarReplicates = true

# The type of weights to use to average peak intensities and rank replicates
# Choices are SN (signal-to-noise), XCORR (SEQUEST Xcorr), PROB (probability)
replicateWeight = SN

  
### QUALITY FILTER ###

# Whether or not to penalize singletons in quality filters
qualityPenalizeSingletons = false

# A probability threshold above which library entries are made immune to quality filters
qualityImmuneProbThreshold = 1.01

# Whether or not to grant immunity to library entries identified with multiple search engines
qualityImmuneMultipleEngines = true
  
#################################################
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info