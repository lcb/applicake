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

class Xinteract(MsMsIdentification):
    """
    Wrapper for the TPP-tool xinteract.
    """

    _input_file = ''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.pepxml' % base
        
    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'xinteract'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        See interface.

        - replace list of PEPXMLs with output of the application
        - create command
        """
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._result_file = os.path.join(wd,self._result_file)
        old = info['PEPXMLS']
        new = self._result_file
        log.debug('replace value of [PEPXMLS] [%s] with [%s]' %(old,new))     
        info['PEPXMLS'] = [new]
        prefix,info = self._get_prefix(info,log)
        command = '%s -N%s %s %s' % (prefix,self._result_file,info['XINTERACT_ARGS'],','.join(old))
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(Xinteract, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'PEPXMLS', 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'XINTERACT_ARGS', 'Arguments for xinteract')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.

        Check the following:
        - if decoy hits were found
        - if exit code was non-zero
        - if job is incomplete
        - if file is valid
        - if xml is well-formed
        """
        exit_code,info = super(Xinteract,self).validate_run(info,log, run_code,out_stream, err_stream)
        if 0 != run_code:
            return exit_code,info
        out_stream.seek(0)
        err_stream.seek(0)
        if 'No decoys with label' in err_stream:
            self.log.error('found no decoy hits')
            return 1,info                   
        if 'exited with non-zero exit code' in out_stream:
            self.log.error('xinteract did not complete with exit code !=0')
            return 1,info
        if 'QUIT - the job is incomplete' in out_stream:
            self.log.error('xinteract: job is incomplete')
            return 1,info        
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info       
        return 0,info
