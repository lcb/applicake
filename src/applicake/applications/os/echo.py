'''
Created on Mar 28, 2012

@author: quandtan
'''

from applicake.framework.interfaces import IWrapper
from applicake.framework.enums import KeyEnum

class Echo(IWrapper):
    """
    Performs echo of an comment that is defined in the input file
    via the key 'COMMENT'
    """
    def prepare_run(self,info,log):
        """
        See interface
        """
        comment = info[KeyEnum.comment_key]
        return ('echo "%s"' % comment,info)
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
        exit_code = 0
        if run_code != 0:
            exit_code = run_code
        else:
            out = out_stream.read()
            if len(out) == 0:
                log.error(
                          '''The output stream did not contain any value.
                          check if the input file contained a value for the key [COMMENT]
                          ''')
                exit_code = 1
        return (exit_code,info)
                
        
