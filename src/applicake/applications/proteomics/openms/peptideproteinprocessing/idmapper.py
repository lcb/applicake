'''
Created on Jun 12, 2012

@author: quandtan
'''

import os
from applicake.applications.proteomics.base import OpenMs
from applicake.framework.templatehandler import BasicTemplateHandler

class IdMapper(OpenMs):
    """
    Wrapper for OpenMS tool IDMapper (only support for CONSENSUSXML)
    """

    _xml_type = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._default_prefix = 'IDMapper'
        self._input_file = '%s.ini' % base # application specific config file
        self._result_file = '%s.CONSENSUSXML' % base # result produced by the application

    def get_template_handler(self):
        """
        See interface
        """
        return IdMapperTemplate()

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
        # have to temporarily set a key in info to store the original CONSENSUSXML        
        info['ORGFEATUREXML'] = info['CONSENSUSXML']
        self._result_file = os.path.join(wd,self._result_file)
        info['CONSENSUSXML'] = self._result_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        # can delete temporary key as it is not longer needed
        del info['ORGFEATUREXML']
        prefix,info = self.get_prefix(info,log)
        command = '%s -ini %s' % (prefix,self._input_file)
        
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(IdMapper, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'CONSENSUSXML', 'The CONSENSUSXML input file'),
        args_handler.add_app_args(log, 'IDXML', 'The idXML input file')
        return args_handler
    

class IdMapperTemplate(BasicTemplateHandler):
    """
    Template handler for IdMapper.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="IDMapper" description="Assigns protein/peptide identifications to features or consensus features.">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;IDMapper&apos;">
      <ITEM name="id" value="$IDXML" type="string" description="Protein/peptide identifications file" tags="input file,required" restrictions="*.idXML" />
      <ITEM name="in" value="$ORGFEATUREXML" type="string" description="Feature map/consensus map file" tags="input file,required" restrictions="*.CONSENSUSXML,*.consensusXML" />
      <ITEM name="out" value="$CONSENSUSXML" type="string" description="Output file (the format depends on the input file format)." tags="output file,required" restrictions="*.CONSENSUSXML,*.consensusXML" />
      <ITEM name="rt_tolerance" value="60" type="float" description="RT tolerance (in seconds) for the matching of peptide identifications and (consensus) features.#br#Tolerance is understood as &apos;plus or minus x&apos;, so the matching range increases by twice the given value." restrictions="0:" />
      <ITEM name="mz_tolerance" value="10" type="float" description="m/z tolerance (in ppm or Da) for the matching of peptide identifications and (consensus) features.#br#Tolerance is understood as &apos;plus or minus x&apos;, so the matching range increases by twice the given value." restrictions="0:" />
      <ITEM name="mz_measure" value="ppm" type="string" description="Unit of &apos;mz_tolerance&apos;." restrictions="ppm,Da" />
      <ITEM name="mz_reference" value="precursor" type="string" description="Source of m/z values for peptide identifications. If &apos;precursor&apos;, the precursor-m/z from the idXML is used. If &apos;peptide&apos;,#br#masses are computed from the sequences of peptide hits; in this case, an identification matches if any of its hits matches.#br#(&apos;peptide&apos; should be used together with &apos;use_centroid_mz&apos; to avoid false-positive matches.)" restrictions="precursor,peptide" />
      <ITEM name="ignore_charge" value="false" type="string" description="For feature/consensus maps: Assign an ID independently of whether its charge state matches that of the (consensus) feature." restrictions="true,false" />
      <ITEM name="use_centroid_rt" value="false" type="string" description="Use the RT coordinates of the feature centroids for matching, instead of the RT ranges of the features/mass traces." restrictions="true,false" />
      <ITEM name="use_centroid_mz" value="false" type="string" description="Use the m/z coordinates of the feature centroids for matching, instead of the m/z ranges of the features/mass traces.#br#(If you choose &apos;peptide&apos; as &apos;mz_reference&apos;, you should usually set this flag to avoid false-positive matches.)" restrictions="true,false" />
      <ITEM name="use_subelements" value="false" type="string" description="Match using RT and m/z of sub-features instead of consensus RT and m/z. A consensus feature matches if any of its sub-features matches." restrictions="true,false" />
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

class OrbiLessStrict(BasicTemplateHandler):
    """
    Template handler for IdMapper.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="IDMapper" description="Assigns protein/peptide identifications to features or consensus features.">
    <ITEM name="version" value="1.8.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;IDMapper&apos;">
      <ITEM name="id" value="$IDXML" type="string" description="Protein/peptide identifications file" tags="input file,required" restrictions="*.idXML" />
      <ITEM name="in" value="$ORGFEATUREXML" type="string" description="Feature map/consensus map file" tags="input file,required" restrictions="*.CONSENSUSXML,*.consensusXML" />
      <ITEM name="out" value="$CONSENSUSXML" type="string" description="Output file (the format depends on the input file format)." tags="output file,required" restrictions="*.featureXML,*.consensusXML" />
       <ITEM name="rt_tolerance" value="5" type="float" description="RT tolerance (in seconds) for the matching of peptide identifications and (consensus) features.#br#Tolerance is understood as &apos;plus or minus x&apos;, so the matching range increases by twice the given value." restrictions="0:" />
      <ITEM name="mz_tolerance" value="40" type="float" description="m/z tolerance (in ppm or Da) for the matching of peptide identifications and (consensus) features.#br#Tolerance is understood as &apos;plus or minus x&apos;, so the matching range increases by twice the given value." restrictions="0:" />
      <ITEM name="mz_measure" value="ppm" type="string" description="Unit of &apos;mz_tolerance&apos;." restrictions="ppm,Da" />
      <ITEM name="mz_reference" value="peptide" type="string" description="Source of m/z values for peptide identifications. If &apos;precursor&apos;, the precursor-m/z from the idXML is used. If &apos;peptide&apos;,#br#masses are computed from the sequences of peptide hits; in this case, an identification matches if any of its hits matches.#br#(&apos;peptide&apos; should be used together with &apos;use_centroid_mz&apos; to avoid false-positive matches.)" restrictions="precursor,peptide" />
      <ITEM name="ignore_charge" value="false" type="string" description="For feature/consensus maps: Assign an ID independently of whether its charge state matches that of the (consensus) feature." restrictions="true,false" />
      <ITEM name="use_centroid_rt" value="false" type="string" description="Use the RT coordinates of the feature centroids for matching, instead of the RT ranges of the features/mass traces." restrictions="true,false" />
      <ITEM name="use_centroid_mz" value="true" type="string" description="Use the m/z coordinates of the feature centroids for matching, instead of the m/z ranges of the features/mass traces.#br#(If you choose &apos;peptide&apos; as &apos;mz_reference&apos;, you should usually set this flag to avoid false-positive matches.)" restrictions="true,false" />
      <ITEM name="use_subelements" value="false" type="string" description="Match using RT and m/z of sub-features instead of consensus RT and m/z. A consensus feature matches if any of its sub-features matches." restrictions="true,false" />
      <ITEM name="log" value="TOPP.log" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
    </NODE>
  </NODE>
</PARAMETERS>
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info