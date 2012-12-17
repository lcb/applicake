'''
Created on Dec 10, 2012

@author: loblum
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils

class Mzxml2Search(IWrapper):
    """
    Wrapper for MzXML2Search (mzXML -> mgf)
    """
    
    def __init__(self):
        self._default_prefix = 'MzXML2Search'
        base = self.__class__.__name__
        self._input_link = '%s.mzXML' % base
        self._result_file = '%s.mgf' % base     


    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info  
       
    
    def prepare_run(self,info,log):
        """
        See interface.
        """
        
        wd = info[self.WORKDIR]
        
        self._input_link = os.path.join(wd,self._input_link)
        os.symlink(info['MZXML'], self._input_link)
        
        self._result_file = os.path.join(wd,self._result_file)
        info['MGF'] = self._result_file
        
        prefix,info = self.get_prefix(info,log)
        command = "%s -mgf %s" %(wd,prefix,self._input_link) 
        return command,info  
    
    def set_args(self,log,args_handler):
        """
        See interface
        """       
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format') 
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')  
        return args_handler      
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
        if 0 != run_code:
            return run_code,info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        return 0,info  

