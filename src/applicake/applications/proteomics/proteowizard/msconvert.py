'''
Created on May 10, 2012

@author: quandtan
'''

from applicake.framework.interfaces import IWrapper

class Mzxml2Mgf(IWrapper):
    """
    Wrapper for msconvert (mzxml -> mgf)
    """
    
    def __init__(self):
        self._default_prefix = 'msconert'


    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info  
    
    def prepare_run(self,info,log):
        """
        See interface
        """
         
        return ('%s ' % (prefix),info)
    
    def set_args(self,log,args_handler):
        """
        See interface
        """    
        args_handler.add_app_args(log, 'MGF', 'Peak list file in mgf format')    
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')       
        return args_handler      
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
