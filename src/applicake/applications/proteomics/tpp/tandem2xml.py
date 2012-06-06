'''
Created on Jun 6, 2012

@author: quandtan
'''

import os
from applicake.applications.proteomics.modifications import ModificationDb
from applicake.applications.proteomics.base import MsMsIdentification
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class Tandem2Xml(MsMsIdentification):
    """
    classdocs
    """


    def __init__(self, params):
        """
        Constructor
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
        return Tandem2XmlTemplate()

    def prepare_run(self,info,log):
        """
        See interface.

    - 
        """            
        prefix,info = self._get_prefix(info,log)
        self._result_filename  = os.path.join(, self.name  + '.pepxml')
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        self.log.debug("add key 'PEPXML' with value [%s] to ini" % self._result_filename)
        return "%s %s %s" % (prefix,input_filename,self._result_filename) 
        command = '%s %s' % (prefix,self._input_file)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler = super(Tandem2Xml, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'XTANDEM_RESULT', 'Result file of an X!Tandem-search.') 
          
        return args_handler
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.

        Check the following:        
        - 
        """  
        exit_code,info = super(Tandem2Xml,self).validate_run(info,log, run_code,out_stream, err_stream)
        if 0 != run_code:
            return exit_code,info   
        out_stream.seek(0)        
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info
        return 0,info  
            