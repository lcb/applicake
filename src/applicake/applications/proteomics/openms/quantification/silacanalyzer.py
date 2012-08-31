'''
Created on Aug 30, 2012

@author: quandtan
'''

import os
from applicake.applications.proteomics.base import OpenMs
from applicake.framework.templatehandler import BasicTemplateHandler

class SilacAnalyzer(OpenMs):
    """
    Wrapper for the OpenMS tools SilacAnalyzer.
    """

    _input_file = ''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._input_file = '%s.ini' % base # application specific config file
        self._result_file = '%s.consensusXML' % base # result produced by the application

    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'SILACAnalyzer'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return SilacAnalyzerTemplate()

    def prepare_run(self,info,log):
        """
        See interface.

        - Read the a specific template and replaces variables from the info object.
        - Tool is executed using the pattern: [PREFIX] -ini [TEMPLATE].
        - If there is a result file, it is added with a specific key to the info object.
        """
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._input_file = os.path.join(wd,self._input_file)
        info['TEMPLATE'] = self._input_file
        self._result_file = os.path.join(wd,self._result_file)
        info['CONSENSUSXML'] = self._result_file
        
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        prefix,info = self._get_prefix(info,log)
        command = '%s -ini %s' % (prefix,self._input_file)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(SilacAnalyzer, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'MZML', 'The input mzML file '),
#        args_handler.add_app_args(log, 'FEATUREXML', 'The output featureXML file '),
        args_handler.add_app_args(log, 'CONSENSUSXML', 'The output featureXML file ')
        args_handler.add_app_args(log, 'MISSEDCLEAVAGE', 'Number of maximal allowed missed cleavages')
        return args_handler


class SilacAnalyzerTemplate(BasicTemplateHandler):
    """
    Template handler for SilacAnalyzer.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="SILACAnalyzer" description="Determination of peak ratios in LC-MS data">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;SILACAnalyzer&apos;">
      <ITEM name="in" value="$MZML" type="string" description="Raw LC-MS data to be analyzed. (Profile data required. Will not work with centroided data!)" tags="input file,required" restrictions="*.mzML" />
      <ITEM name="out" value="$CONSENSUSXML" type="string" description="Set of all identified peptide groups (i.e. peptide pairs or triplets or singlets or ..). The m/z-RT positions correspond to the lightest peptide in each group." tags="output file" restrictions="*.consensusXML" />
      <ITEM name="out_clusters" value="" type="string" description="Optional debug output containing data points passing all filters, hence belonging to a SILAC pattern. Points of the same colour correspond to the mono-isotopic peak of the lightest peptide in a pattern." tags="advanced,output file" restrictions="*.consensusXML" />
      <ITEM name="out_features" value="" type="string" description="Optional output file containing the individual peptide features in &apos;out&apos;." tags="advanced,output file" restrictions="*.featureXML" />
      <ITEM name="out_filters" value="" type="string" description="Optional output file containing all points that passed the filters as txt. Suitable as input for &apos;in_filters&apos; to perform clustering without preceding filtering process." tags="advanced,output file" restrictions="*.consensusXML" />
      <ITEM name="in_filters" value="" type="string" description="Optional input file containing all points that passed the filters as txt. Use output from &apos;out_filters&apos; to perform clustering only." tags="advanced,output file" restrictions="*.consensusXML" />
      <ITEM name="out_debug" value="" type="string" description="Filename base for debug output." tags="advanced" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="$THREADS" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      <NODE name="algorithm" description="Parameters for the algorithm.">
        <ITEM name="allow_missing_peaks" value="true" type="string" description="Low intensity peaks might be missing from the isotopic pattern of some of the peptides. Should such peptides be included in the analysis?" tags="advanced" restrictions="true,false" />
        <ITEM name="rt_threshold" value="30" type="float" description="Typical retention time [s] over which a characteristic peptide elutes. (This is not an upper bound. Peptides that elute for longer will be reported.)" restrictions="0:" />
        <ITEM name="rt_min" value="1" type="float" description="Lower bound for the retention time [s]." restrictions="0:" />
        <ITEM name="intensity_cutoff" value="10000" type="float" description="Lower bound for the intensity of isotopic peaks in a SILAC pattern." restrictions="0:" />
        <ITEM name="intensity_correlation" value="0.6" type="float" description="Lower bound for the Pearson correlation coefficient, which measures how well intensity profiles of different isotopic peaks correlate." restrictions="0:1" />
        <ITEM name="model_deviation" value="5" type="float" description="Upper bound on the factor by which the ratios of observed isotopic peaks are allowed to differ from the ratios of the theoretic averagine model, i.e. ( theoretic_ratio / model_deviation ) &lt; observed_ratio &lt; ( theoretic_ratio * model_deviation )." restrictions="1:" />
      </NODE>
      <NODE name="labels" description="Isotopic labels that can be specified in section &apos;sample&apos;.">
        <ITEM name="Arg6" value="6.0201290268" type="float" description="Arg6 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Arg10" value="10.0082686" type="float" description="Arg10 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Lys4" value="4.0251069836" type="float" description="Lys4 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Lys6" value="6.0201290268" type="float" description="Lys6 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Lys8" value="8.0141988132" type="float" description="Lys8 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="dICPL4" value="4.025107" type="float" description="mass difference between isotope-coded protein labels ICPL 4 and ICPL 0" tags="advanced" restrictions="0:" />
        <ITEM name="dICPL6" value="6.020129" type="float" description="mass difference between isotope-coded protein labels ICPL 6 and ICPL 0" tags="advanced" restrictions="0:" />
        <ITEM name="dICPL10" value="10.045236" type="float" description="mass difference between isotope-coded protein labels ICPL 10 and ICPL 0" tags="advanced" restrictions="0:" />
        <ITEM name="Methyl4" value="4.0202" type="float" description="Methyl4 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Methyl8" value="8.0202" type="float" description="Methyl8 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Methyl12" value="12.0202" type="float" description="Methyl12 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Methyl16" value="16.0202" type="float" description="Methyl16 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Methyl24" value="24.0202" type="float" description="Methyl24 mass shift" tags="advanced" restrictions="0:" />
        <ITEM name="Methyl32" value="32.0202" type="float" description="Methyl32 mass shift" tags="advanced" restrictions="0:" />
      </NODE>
      <NODE name="sample" description="Parameters describing the sample and its labels.">
        <ITEM name="labels" value="[Lys8,Arg10]" type="string" description="Labels used for labelling the sample. [...] specifies the labels for a single sample. For example, [Lys4,Arg6][Lys8,Arg10] describes a mixtures of three samples. One of them unlabelled, one labelled with Lys4 and Arg6 and a third one with Lys8 and Arg10. For permitted labels see &apos;advanced parameters&apos;, section &apos;labels&apos;. If left empty the tool identifies singlets, i.e. acts as peptide feature finder." />
        <ITEM name="charge" value="1:5" type="string" description="Range of charge states in the sample, i.e. min charge : max charge." />
        <ITEM name="missed_cleavages" value="$MISSEDCLEAVAGE" type="int" description="Maximum number of missed cleavages." restrictions="0:" />
        <ITEM name="peaks_per_peptide" value="3:6" type="string" description="Range of peaks per peptide in the sample, i.e. min peaks per peptide : max peaks per peptide. For example 3:6, if isotopic peptide patterns in the sample consist of either three, four, five or six isotopic peaks. " tags="advanced" />
      </NODE>
    </NODE>
  </NODE>
</PARAMETERS>
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
