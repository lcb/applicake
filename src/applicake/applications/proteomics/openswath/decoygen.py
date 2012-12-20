'''
Created on Oct 24, 2012

@author: lorenz
'''
import os, re

from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils

class OpenSwathDecoyGenerator(IWrapper):
    _default_prefix = 'OpenSwathDecoyGenerator'
    _result_file = 'OpenSwathDecoyGenerator.TraML'
    
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        self._result_file = os.path.join(info[self.WORKDIR],self._result_file)
        
        if info['SWDECOY_THEORETICAL'].upper() == 'TRUE':
            theoretical = '-theoretical'
        else:
            theoretical = ''
            
        prefix,info = self.get_prefix(info,log)
        command = '%s -in %s -out %s -method %s -append -exclude_similar %s' % (prefix,
                                                                                info[self.TRAML],
                                                                                self._result_file,
                                                                                info['SWDECOY_METHOD'],
                                                                                theoretical)
        return command,info

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.TRAML, 'input traml')
        args_handler.add_app_args(log, 'SWDECOY_METHOD', 'decoy generation method',choices=['shuffle','pseudo-reverse','reverse','shift'])
        args_handler.add_app_args(log, 'SWDECOY_THEORETICAL', 'Set true if only annotated transitions should be used and be corrected to the theoretical mz')
        args_handler.add_app_args(log, self.WORKDIR, 'working directory')        
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1,info
        
        info[self.TRAML] = self._result_file   
        return 0,info
    