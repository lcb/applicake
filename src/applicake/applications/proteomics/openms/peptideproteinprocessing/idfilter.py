'''
Created on Jun 10, 2012

@author: quandtan
'''

from applicake.applications.proteomics.base import PeptideProteinPreprocessing
from applicake.framework.templatehandler import BasicTemplateHandler

class IdFilter(PeptideProteinPreprocessing):
    """
    Wrapper for the OpenMS tools IDFilter.
    """

    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = ''
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return IdFilterTemplate()

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(IdFilter, self).set_args(log,args_handler)
        args_handler.add_app_args(log, '', '')
        return args_handler


class IdFilterTemplate(BasicTemplateHandler):
    """
    Template handler for IdFilter.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="IDFilter" description="Filters results from protein or peptide identification engines based on different criteria.">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;IDFilter&apos;">
      <ITEM name="in" value="" type="string" description="input file " tags="input file,required" restrictions="*.idXML" />
      <ITEM name="out" value="" type="string" description="output file " tags="output file,required" restrictions="*.idXML" />
      <ITEM name="min_length" value="0" type="int" description="Keep only peptide hits with a length greater or equal this value." restrictions="0:" />
      <ITEM name="unique" value="false" type="string" description="If a peptide hit occurs more than once, only one instance is kept. This will (for instance) remove                             redundant identifications from multiple charge states or concurrent CID+HCD spectra.                             If you are aiming towards quantitation, you probably do *not* want to use this flag!" restrictions="true,false" />
      <ITEM name="unique_per_protein" value="false" type="string" description="Only peptides matching exactly one protein are kept. Remember that isoforms count as different proteins!" restrictions="true,false" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="$THREADS" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      <NODE name="score" description="Filtering by peptide/protein score">
        <ITEM name="pep" value="0.01" type="float" description="The score which should be reached by a peptide hit to be kept. The score is dependent on the most recent(!) preprocessing - it could be Mascot scores (if a MascotAdapter was applied before), or an FDR (if FalseDiscoveryRate was applied before), etc." />
        <ITEM name="prot" value="0" type="float" description="The score which should be reached by a protein hit to be kept." />
      </NODE>
      <NODE name="thresh" description="Filtering by significance threshold">
        <ITEM name="pep" value="0" type="float" description="Keep a peptide hit only if its score is above this fraction of the peptide significance threshold." />
        <ITEM name="prot" value="0" type="float" description="Keep a protein hit only if its score is above this fraction of the protein significance threshold." />
      </NODE>
      <NODE name="whitelist" description="Filtering by whitelisting (only instances also present in a whitelist file can pass)">
        <ITEM name="proteins" value="" type="string" description="filename of a FASTA file containing protein sequences.#br#All peptides that are not a substring of a sequence in this file are removed#br#All proteins whose accession is not present in this file are removed." tags="input file" restrictions="*.FASTA" />
        <ITEM name="by_seq_only" value="false" type="string" description="Match peptides with FASTA file by sequence instead of accession and disable protein filtering." restrictions="true,false" />
      </NODE>
      <NODE name="blacklist" description="Filtering by blacklisting (only instances not present in a blacklist file can pass)">
        <ITEM name="peptides" value="" type="string" description="Peptides having the same sequence as any peptide in this file will be filtered out#br#" tags="input file" restrictions="*.idXML" />
      </NODE>
      <NODE name="rt" description="Filtering by RT predicted by &apos;RTPredict&apos;">
        <ITEM name="p_value" value="0" type="float" description="Retention time filtering by the p-value predicted by RTPredict." restrictions="0:1" />
        <ITEM name="p_value_1st_dim" value="0" type="float" description="Retention time filtering by the p-value predicted by RTPredict for first dimension." restrictions="0:1" />
      </NODE>
      <NODE name="best" description="Filtering best hits per spectrum (for peptides) or from proteins">
        <ITEM name="n_peptide_hits" value="0" type="int" description="Keep only the &apos;n&apos; highest scoring peptide hits per spectrum (for n&gt;0)." restrictions="0:" />
        <ITEM name="n_protein_hits" value="0" type="int" description="Keep only the &apos;n&apos; highest scoring protein hits (for n&gt;0)." restrictions="0:" />
        <ITEM name="strict" value="false" type="string" description="Keep only the highest scoring peptide hit.#br#Similar to n_peptide_hits=1, but if there are two or more highest scoring hits, none are kept." restrictions="true,false" />
      </NODE>
    </NODE>
  </NODE>
</PARAMETERS>

"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info