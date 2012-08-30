'''
Created on Aug 30, 2012

@author: quandtan
'''

import os
from applicake.applications.proteomics.base import OpenMs
from applicake.framework.templatehandler import BasicTemplateHandler

class ProteinQuantifier(OpenMs):
    """
    Wrapper for the OpenMS tools ProteinQuanifier.
    """

    _input_file = ''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._input_file = '%s.ini' % base # application specific config file
        self._result_file = '%s.result' % base # result produced by the application

    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = ''
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return ProteinQuantifierTemplate()

    def prepare_run(self,info,log):
        """
        See interface.

        - Read the a specific template and replaces variables from the info object.
        - Tool is executed using the pattern: [PREFIX] -ini [TEMPLATE].
        - If there is a result file, it is added with a specific key to the info object.
        """
        key = 'IDXML'
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        self._result_file = os.path.join(wd,self._result_file)
        # have to temporarily set a key in info to store the original IDXML
        info['ORG%s'% key] = info[key]
        info[key] = self._result_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        # can delete temporary key as it is not longer needed
        del info['ORG%s' % key]
        prefix,info = self.get_prefix(info,log)
        command = '%s -ini %s' % (prefix,self._template_file)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(ProteinQuantifier, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'IDXML', 'The input %s file' % self._file_type)
        args_handler.add_app_args(log, 'CONSENSUSXML', 'The input featureXML file ')
        return args_handler


class ProteinQuantifierTemplate(BasicTemplateHandler):
    """
    Template handler for ProteinQuantifier.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="ProteinQuantifier" description="Compute peptide and protein abundances">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;ProteinQuantifier&apos;">
      <ITEM name="in" value="$CONSENSUSXML" type="string" description="Input file" tags="input file,required" restrictions="*.featureXML,*.consensusXML" />
      <ITEM name="protxml" value="$ORGIDXML" type="string" description="ProteinProphet results (protXML converted to idXML) for the identification runs that were used to annotate the input.#br#Information about indistinguishable proteins will be used for protein quantification." tags="input file" restrictions="*.idXML" />
      <ITEM name="out" value="proteins.txt" type="string" description="Output file for protein abundances" tags="output file" />
      <ITEM name="peptide_out" value="peptides.txt" type="string" description="Output file for peptide abundances" tags="output file" />
      <ITEM name="id_out" value="$IDXML" type="string" description="Output file for peptide and protein abundances (annotated idXML) - suitable for export to mzTab.#br#Either &apos;out&apos;, &apos;peptide_out&apos;, or &apos;id_out&apos; are required. They can be used together." tags="output file" restrictions="*.idXML" />
      <ITEM name="top" value="1" type="int" description="Calculate protein abundance from this number of proteotypic peptides (most abundant first; &apos;0&apos; for all)" restrictions="0:" />
      <ITEM name="average" value="median" type="string" description="Averaging method used to compute protein abundances from peptide abundances" restrictions="median,mean,sum" />
      <ITEM name="include_all" value="false" type="string" description="Include results for proteins with fewer proteotypic peptides than indicated by &apos;top&apos; (no effect if &apos;top&apos; is 0 or 1)" restrictions="true,false" />
      <ITEM name="filter_charge" value="false" type="string" description="Distinguish between charge states of a peptide. For peptides, abundances will be reported separately for each charge;#br#for proteins, abundances will be computed based only on the most prevalent charge of each peptide.#br#By default, abundances are summed over all charge states." restrictions="true,false" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      <NODE name="consensus" description="Additional options for consensus maps">
        <ITEM name="normalize" value="false" type="string" description="Scale peptide abundances so that medians of all samples are equal" restrictions="true,false" />
        <ITEM name="fix_peptides" value="false" type="string" description="Use the same peptides for protein quantification across all samples.#br#With &apos;top 0&apos;, all peptides that occur in every sample are considered.#br#Otherwise (&apos;top N&apos;), the N peptides that occur in the most samples (independently of each other) are selected,#br#breaking ties by total abundance (there is no guarantee that the best co-ocurring peptides are chosen!)." restrictions="true,false" />
      </NODE>
      <NODE name="format" description="Output formatting options">
        <ITEM name="separator" value="," type="string" description="Character(s) used to separate fields; by default, the &apos;tab&apos; character is used" />
        <ITEM name="quoting" value="double" type="string" description="Method for quoting of strings: &apos;none&apos; for no quoting, &apos;double&apos; for quoting with doubling of embedded quotes,#br#&apos;escape&apos; for quoting with backslash-escaping of embedded quotes" restrictions="none,double,escape" />
        <ITEM name="replacement" value="_" type="string" description="If &apos;quoting&apos; is &apos;none&apos;, used to replace occurrences of the separator in strings before writing" />
      </NODE>
    </NODE>
  </NODE>
</PARAMETERS>

"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info