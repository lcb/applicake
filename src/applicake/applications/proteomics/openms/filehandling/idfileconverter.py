'''
Created on Jun 9, 2012

@author: quandtan
'''

import os
import sys
from applicake.applications.proteomics.base import OpenMs
from applicake.framework.templatehandler import BasicTemplateHandler


class PepXml2IdXml(OpenMs):
    """
    Specific implementation if the IdFileConverter class to convert files in pepXML to idXML format.
    """
      
    _input_file = ''
    _result_file = ''
      
    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._input_file = '%s.ini' % base # application specific config file
        self._result_file = '%s.idXML' % base # result produced by the application    
    
    def get_prefix(self,info,log):
            if not info.has_key(self.PREFIX):
                info[self.PREFIX] = 'IDFileConverter'
                log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
            return info[self.PREFIX],info
    
    def get_template_handler(self):
        """
        See interface
        """
        return PepXml2IdXmlTemplate()    
    
    def prepare_run(self,info,log):
        """
        See interface.

        - Read the a specific template and replaces variables from the info object.
        - Tool is executed using the pattern: [PREFIX] -ini [TEMPLATE].
        - If there is a result file, it is added with a specific key to the info object.
        """
        if len(info['PEPXMLS']) != 1:
            log.fatal('Only the use of 1 pepXML file is currently supported. Found [%s]' % info['PEPXMLS'])
            sys.exit(1)        
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._input_file = os.path.join(wd,self._input_file)
        info[self.TEMPLATE] = self._input_file
        self._result_file = os.path.join(wd,self._result_file)
        info['IDXML'] = self._result_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        #need to convert PEPXMLS from list to a string (1st element)
        # because program only handles single pepxmls
        pepxmls = info['PEPXMLS']
        info['PEPXMLS'] = pepxmls[0]
        mod_template,info = th.modify_template(info, log)
        # reset PEPXMLS to original value
        info['PEPXMLS'] = pepxmls
        prefix,info = self.get_prefix(info,log)
        command = '%s -ini %s' % (prefix,self._input_file)
        return command,info      

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(PepXml2IdXml, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'PEPXMLS', 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')  
        return args_handler  
  

class PepXml2IdXmlTemplate(BasicTemplateHandler):
    """
    Template handler for IdFileConverter (PepXML -> IdXML).
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="IDFileConverter" description="Converts identification engine file formats.">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;IDFileConverter&apos;">
      <ITEM name="in" value="$PEPXMLS" type="string" description="Input file or directory containing the output of the search engine.#br#Sequest: Directory containing the .out files#br#pepXML: Single pepXML file.#br#protXML: Single protXML file.#br#xml: Single mascot XML file.#br#idXML: Single idXML file.#br#" tags="input file,required" />
      <ITEM name="out" value="$IDXML" type="string" description="Output file" tags="output file,required" restrictions="*.idXML,*.mzid,*.pepXML,*.FASTA" />
      <ITEM name="out_type" value="" type="string" description="output file type -- default: determined from file extension or content#br#" restrictions="idXML,mzid,pepXML,FASTA" />
      <ITEM name="mz_file" value="$MZXML" type="string" description="MS data file from which the pepXML was generated. Used to look up retention times (some pepXMLs contain only scan numbers) and/or to define what parts to extract (some pepXMLs contain results from multiple experiments)." />
      <ITEM name="ignore_proteins_per_peptide" value="false" type="string" description="Workaround to deal with .out files that contain e.g. &quot;+1&quot; in references column,#br#but do not list extra references in subsequent lines (try -debug 3 or 4)" tags="advanced" restrictions="true,false" />
      <ITEM name="mz_name" value="" type="string" description="Experiment filename/path to match in the pepXML file (&apos;base_name&apos; attribute). Only necessary if different from &apos;mz_file&apos;." />
      <ITEM name="use_precursor_data" value="false" type="string" description="Use precursor RTs (and m/z values) from &apos;mz_file&apos; for the generated peptide identifications, instead of the RTs of MS2 spectra." restrictions="true,false" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="$THREADS" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
    </NODE>
  </NODE>
</PARAMETERS>
"""
        return template,info