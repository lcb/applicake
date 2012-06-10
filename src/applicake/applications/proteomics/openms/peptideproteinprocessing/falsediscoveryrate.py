'''
Created on Jun 9, 2012

@author: quandtan
'''

from applicake.applications.proteomics.base import PeptideProteinPreprocessing
from applicake.framework.templatehandler import BasicTemplateHandler

class FalseDiscoveryRate(PeptideProteinPreprocessing):
    """
    Wrapper for the OpenMS tools FalseDiscoveryRate.
    """

    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'FalseDiscoveryRate'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return FalseDiscoveryRateTemplate()

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(FalseDiscoveryRate, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'DECOY_STRING', 'Prefix to indicate decoy entries in a Protein sequence database.')
        return args_handler


class FalseDiscoveryRateTemplate(BasicTemplateHandler):
    """
    Template handler for FalseDiscoveryRate.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="FalseDiscoveryRate" description="Estimates the false discovery rate on peptide and protein level using decoy searches.">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;FalseDiscoveryRate&apos;">
      <ITEM name="in" value="$ORGIDXML" type="string" description="Identification input file which contains a search against a concatenated sequence database" tags="input file" restrictions="*.idXML" />
      <ITEM name="fwd_in" value="" type="string" description="Identification input to estimate FDR, forward" tags="input file" restrictions="*.idXML" />
      <ITEM name="rev_in" value="" type="string" description="Identification input to estimate FDR, decoy run" tags="input file" restrictions="*.idXML" />
      <ITEM name="out" value="$IDXML" type="string" description="Identification output with annotated FDR" tags="output file,required" restrictions="*.idXML" />
      <ITEM name="proteins_only" value="false" type="string" description="If set, the FDR of the proteins only is calculated" restrictions="true,false" />
      <ITEM name="peptides_only" value="false" type="string" description="If set, the FDR of the peptides only is calculated" restrictions="true,false" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="$THREADS" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      <NODE name="algorithm" description="Parameter section for the FDR calculation algorithm">
        <ITEM name="q_value" value="true" type="string" description="If &apos;true&apos;, the q-values will be calculated instead of the FDRs" restrictions="true,false" />
        <ITEM name="use_all_hits" value="false" type="string" description="If &apos;true&apos; not only the first hit, but all are used (peptides only)" restrictions="true,false" />
        <ITEM name="split_charge_variants" value="false" type="string" description="If set to &apos;true&apos; charge variants are treated separately (for peptides of combined target/decoy searches only)." restrictions="true,false" />
        <ITEM name="treat_runs_separately" value="false" type="string" description="If set to &apos;true&apos; different search runs are treated separately (for peptides of combined target/decoy searches only)." restrictions="true,false" />
        <ITEM name="decoy_string" value="$DECOY_STRING" type="string" description="String which is appended at the accession of the protein to indicate that it is a decoy protein (for proteins only)." />
        <ITEM name="add_decoy_peptides" value="false" type="string" description="If set to true, decoy peptides will be written to output file, too. The q-value is set to the closest target score." restrictions="true,false" />
      </NODE>
    </NODE>
  </NODE>
</PARAMETERS>
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info