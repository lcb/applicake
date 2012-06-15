'''
Created on Jun 15, 2012

@author: quandtan
'''

from applicake.applications.proteomics.base import FeatureXmlModifier
from applicake.framework.templatehandler import BasicTemplateHandler

class IdConflictResolver(FeatureXmlModifier):
    """
    Wrapper for the OpenMS tools IDConflictResolver.
    """

    def __init__(self):
        """
        Constructor
        """
        super(IdConflictResolver,self).__init__()
        self._default_prefix = 'IDConflictResolver ' # default prefix, usually the name of the OpenMS-tool


    def get_template_handler(self):
        """
        See interface
        """
        return IdConflictResolverTemplate()


    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(IdConflictResolver, self).set_args(log,args_handler)
        return args_handler


class IdConflictResolverTemplate(BasicTemplateHandler):
    """
    Template handler for IdConflictResolver.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="IDConflictResolver" description="Resolves ambiguous annotations of features with peptide identifications">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;IDConflictResolver&apos;">
      <ITEM name="in" value="$ORGFEATUREXML" type="string" description="Input file (data annotated with identifications)" tags="input file,required" restrictions="*.featureXML,*.consensusXML" />
      <ITEM name="out" value="$FEATUREXML" type="string" description="Output file (data with one peptide identification per feature)" tags="output file,required" restrictions="*.featureXML,*.consensusXML" />
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