'''
Created on Apr 29, 2012

@author: quandtan
'''
from applicake.applications.proteomics.openms.base import BasicOpenmsWrapper
from applicake.framework.templatehandler import BasicTemplateHandler

class FileConverter(BasicOpenmsWrapper):
    """"
    File converter of OpenMS.
    """
    
    def get_template_handler(self):
        """
        See super class
        """
        return BasicTemplateHandler()

    def get_tool(self):
        """
        See super class.
        """
        return 'FileConverter'


class Mzxml2Mzml(FileConverter):
    """
    Convert mzXML to mzML.
    """
    def get_template_handler(self):
        """
        See super class.
        """
        return Mzxml2MzmlTemplate()

class Mzxml2MzmlTemplate(BasicTemplateHandler):
    """
    Template handler for FileConverter that converts mzXML to mzML.
    
    @precondition: Replaces the variables $MZXML and $MZML    
    """
    
    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="FileConverter" description="Converts between different MS file formats.">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;FileConverter&apos;">
      <ITEM name="in" value="$MZXML" type="string" description="input file " tags="input file,required" restrictions="*.mzData,*.mzXML,*.mzML,*.DTA,*.DTA2D,*.mgf,*.featureXML,*.consensusXML,*.ms2,*.fid,*.tsv,*.peplist,*.kroenik,*.edta" />
      <ITEM name="in_type" value="mzXML" type="string" description="input file type -- default: determined from file extension or content#br#" restrictions="mzData,mzXML,mzML,DTA,DTA2D,mgf,featureXML,consensusXML,ms2,fid,tsv,peplist,kroenik,edta" />
      <ITEM name="out" value="$MZML" type="string" description="output file " tags="output file,required" restrictions="*.mzData,*.mzXML,*.mzML,*.DTA2D,*.mgf,*.featureXML,*.consensusXML" />
      <ITEM name="out_type" value="mzML" type="string" description="output file type -- default: determined from file extension or content#br#" restrictions="mzData,mzXML,mzML,DTA2D,mgf,featureXML,consensusXML" />
      <ITEM name="TIC_DTA2D" value="false" type="string" description="Export the TIC instead of the entire experiment in mzML/mzData/mzXML -&gt; DTA2D conversions." tags="advanced" restrictions="true,false" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
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
            