'''
Created on Nov 12, 2012

@author: lorenz
'''

import os
from applicake.applications.proteomics.base import OpenMs
from applicake.framework.templatehandler import BasicTemplateHandler

class Mzxmls2Mzmls(OpenMs):
    """
    Specific implementation of the FileConverter tool to convert files in mzXML to mzML format.
    """

    def __init__(self):
        """
        Constructor
        """
        self._default_prefix = 'FileConverter'


    def get_template_handler(self):
        """
        See interface
        """
        return Mzxml2MzmlTemplate()

    def prepare_run(self,info,log):
        """
        Builds an AND concatenated command which converts all mzXML to mzML one after the other 
        (fileconvert cannot handle multiple at once)
        the resulting mzMLs are stored in a list with key MZML
        """
        wd = info[self.WORKDIR]
        prefix,info = self.get_prefix(info,log)
        th = self.get_template_handler()
        
        
        mzmls = []
        commands = []
        for mzxml in info['MZXML']:
            infocopy = info.copy()
            fileName, fileExtension = os.path.splitext(os.path.basename(mzxml))
            infocopy[self.TEMPLATE] = os.path.join(wd,fileName+'.ini')
            infocopy['MZXML'] = mzxml
            infocopy['MZML'] = os.path.join(wd,fileName+'.mzML')   
            mod_template,infocopy = th.modify_template(infocopy, log)
            
            mzmls.append(infocopy['MZML'])     
            command = '%s -ini %s' % (prefix,infocopy[self.TEMPLATE])
            commands.append(command)
        
        info['MZML'] = mzmls
        command = ' && '.join(commands)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(Mzxmls2Mzmls, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'MZXML', 'Path to the mzXML fileS.')
        return args_handler


class Mzxml2MzmlTemplate(BasicTemplateHandler):
    """
    Template handler for Mzxml2Mzml.
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
      <ITEM name="in_type" value="" type="string" description="input file type -- default: determined from file extension or content#br#" restrictions="mzData,mzXML,mzML,DTA,DTA2D,mgf,featureXML,consensusXML,ms2,fid,tsv,peplist,kroenik,edta" />
      <ITEM name="out" value="$MZML" type="string" description="output file " tags="output file,required" restrictions="*.mzData,*.mzXML,*.mzML,*.DTA2D,*.mgf,*.featureXML,*.consensusXML" />
      <ITEM name="out_type" value="" type="string" description="output file type -- default: determined from file extension or content#br#" restrictions="mzData,mzXML,mzML,DTA2D,mgf,featureXML,consensusXML" />
      <ITEM name="TIC_DTA2D" value="false" type="string" description="Export the TIC instead of the entire experiment in mzML/mzData/mzXML -&gt; DTA2D conversions." tags="advanced" restrictions="true,false" />
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