'''
Created on Oct 30, 2012

@author: quandtan
'''

import os
from applicake.applications.proteomics.base import OpenMs
from applicake.framework.templatehandler import BasicTemplateHandler

class ConvertTSVToTraML(OpenMs):
    """
    classdocs
    """

    _input_file = ''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._input_file = '%s.ini' % base # application specific config file
        self._result_file = '%s.TraML' % base # result produced by the application

    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'ConvertTSVToTraML'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return ConvertTSVToTraMLTemplate()

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
        info[self.TRAML] = self._result_file
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
        args_handler = super(ConvertTSVToTraML, self).set_args(log,args_handler)
        args_handler.add_app_args(log, '', '')
        return args_handler


class ConvertTSVToTraMLTemplate(BasicTemplateHandler):
    """
    Template handler for ConvertTSVToTraML.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.3" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="ConvertTSVToTraML" description="Converts a csv into a TraML file">
    <ITEM name="version" value="1.9.0" type="string" description="Version of the tool that generated this parameters file." tags="advanced" />
    <NODE name="1" description="Instance &apos;1&apos; section for &apos;ConvertTSVToTraML&apos;">
      <ITEM name="in" value="$TRACSV" type="string" description="transition file (&apos;csv&apos;)" tags="input file,required" />
      <ITEM name="out" value="$TRAML" type="string" description="output file" tags="output file,required" restrictions="*.TraML" />
      <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
      <ITEM name="debug" value="100" type="int" description="Sets the debug level" tags="advanced" />
      <ITEM name="threads" value="$THREADS" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
      <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
      <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
    </NODE>
  </NODE>
</PARAMETERS>
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info