'''
Created on Jun 6, 2012

@author: quandtan
'''

import os
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator
from applicake.framework.interfaces import IWrapper

class InterProphet(IWrapper):
    """
    Wrapper for the TPP-tool InterProphetParser.
    """

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.pepXML' % base # result produced by the application
        
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'InterProphetParser'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        See interface.
        """
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._result_file = os.path.join(wd,self._result_file)
        old = info['PEPXMLS']
        new = self._result_file
        log.debug('replace value of [PEPXMLS] [%s] with [%s]' %(old,new))     
        info['PEPXMLS'] = [new]
        prefix,info = self.get_prefix(info,log)
        command = '%s %s %s %s' % (prefix,info['IPROPHET_ARGS'],' '.join(old),new)    
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files') 
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory') 
        args_handler.add_app_args(log, 'PEPXMLS', 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'IPROPHET_ARGS', 'Arguments for InterProphetParser')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.

        Check the following:
        -
        """
        exit_code,info = super(InterProphet,self).validate_run(info,log, run_code,out_stream, err_stream)
        if 0 != run_code:
            return exit_code,info
        err_stream.seek(0)
        for line in err_stream.readlines():
            if 'fin: error opening' in line:
                self.log.error("could not read the input file [%s]" % self._pepxml_filename)
                return 1,info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info
        return 0,info
