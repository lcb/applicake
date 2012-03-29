'''
Created on Mar 28, 2012

@author: quandtan
'''

from applicake.framework.interfaces import IWrapper

class Echo(IWrapper):
    """
    Performs echo of an comment that is defined in the input file
    via the key 'COMMENT'
    """
    def prepare_run(self,config,log):
        """
        See interface
        """
        comment = config['COMMENT']
        return 'echo "%s"' % comment
    
    def validate_run(self,run_code,log, out_stream, err_stream):
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
        return exit_code
                
        
