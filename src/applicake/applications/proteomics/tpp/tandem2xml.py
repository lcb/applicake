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


    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.result' % base # result produced by the application

    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'Tandem2XML'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info  

    def prepare_run(self,info,log):
        """
        See interface.

        - 
        """            
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._result_file = os.path.join(wd,self._result_file) 
        info['PEPXML'] = self._result_file
        prefix,info = self._get_prefix(info,log)

        command = '%s %s %s' % (prefix,info['XTANDEM_RESULT'],self._result_file)
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
            