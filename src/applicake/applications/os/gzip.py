#!/usr/bin/env python
'''
Created on Dez 20, 2012

@author: lorenz
'''

from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils

class Gzip(IWrapper):
    """
    Performs gzip, checks outfile  
    """
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'COMPRESS', 'File(s) to compress')
        return args_handler
    
    def prepare_run(self, info, log):
        """
        See super class.
        
        @precondition: 'info' object has to contain 'COMPRESS'
        """
        if not isinstance(info['COMPRESS'],list):
            info['COMPRESS'] = [info['COMPRESS']]

        param = ""
        outs = []
        for file in info['COMPRESS']:
            param = param + ' ' + file
            outs.append(file + '.gz')
             
        command = "gzip -v %s" % param
        
        info['COMPRESS_OUT'] = outs
        return command,info
           
    def validate_run(self,info,log, run_code,out_stream, err_stream): 
        if 0 != run_code:
            return run_code,info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info 
        return 0,info
