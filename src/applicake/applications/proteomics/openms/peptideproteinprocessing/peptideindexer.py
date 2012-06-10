'''
Created on Jun 10, 2012

@author: quandtan
'''

from applicake.applications.proteomics.base import PeptideProteinPreprocessing
from applicake.framework.templatehandler import BasicTemplateHandler

class PeptideIndexer(PeptideProteinPreprocessing):
    """
    Wrapper for the OpenMS tools PeptideIndexer.
    """

    def __init__(self):
        """
        Constructor
        """
        super(PeptideIndexer,self).__init__()
        self._default_prefix = 'PeptideIndexer' # default prefix, usually the name of the OpenMS-tool

    def get_template_handler(self):
        """
        See interface
        """
        return PeptideIndexerTemplate()

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(PeptideIndexer, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'DECOY_STRING', 'Prefix to indicate decoy entries in a Protein sequence database.')
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file with target/decoy entries')
        return args_handler


class PeptideIndexerTemplate(BasicTemplateHandler):
    """
    Template handler for PeptideIndexer.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="PeptideIndexer" description="Refreshes the protein references for all peptide hits.">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;PeptideIndexer&apos;">
      <ITEM name="in" value="$ORGIDXML" type="string" description="Input idXML file containing the identifications." tags="input file,required" restrictions="*.IdXML" />
      <ITEM name="fasta" value="$DBASE" type="string" description="Input sequence database in FASTA format. Non-existing relative file-names are looked up via&apos;OpenMS.ini:id_db_dir&apos;" tags="input file,required" restrictions="*.fasta" />
      <ITEM name="out" value="$IDXML" type="string" description="Output idXML file." tags="output file,required" restrictions="*.IdXML" />
      <ITEM name="decoy_string" value="$DECOY_STRING" type="string" description="String that was appended to the accession of the protein database to indicate a decoy protein." />
      <ITEM name="write_protein_sequence" value="true" type="string" description="If set, the protein sequences are stored as well." restrictions="true,false" />
      <ITEM name="prefix" value="true" type="string" description="If set, the decoy_string is supposed to be appended as a prefix." restrictions="true,false" />
      <ITEM name="keep_unreferenced_proteins" value="false" type="string" description="If set, protein hits which are not referenced by any peptide are kept." restrictions="true,false" />
      <ITEM name="allow_unmatched" value="false" type="string" description="If set, unmatched peptide sequences are allowed. By default (i.e. not set) the program terminates with error status on unmatched peptides." restrictions="true,false" />
      <ITEM name="aaa_max" value="4" type="int" description="Maximal number of ambiguous amino acids (AAA) allowed when matching to a protein DB with AAA&apos;s. AAA&apos;s are &apos;B&apos;, &apos;Z&apos;, and &apos;X&apos;" restrictions="0:" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="$THREADS" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
    </NODE>
  </NODE>
</PARAMETERS>
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info