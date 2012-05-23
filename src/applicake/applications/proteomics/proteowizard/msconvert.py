'''
Created on May 10, 2012

@author: quandtan
'''

from applicake.framework.interfaces import IWrapper

class Msconvert(IWrapper):
    """
    
    """
    def prepare_run(self,info,log):
        """
        See interface
        """
        try:
            prefix = info[self.prefix_key]
        except:
            log.fatal('did not find one of the keys [%s]' % (self.prefix_key))
            return '' 
        
          
        return ('%s ' % (prefix),info)
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
