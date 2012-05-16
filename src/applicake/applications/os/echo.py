#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: quandtan
'''

from applicake.framework.interfaces import IWrapper
from applicake.framework.argshandler import ArgsHandler

class Echo(IWrapper):
    """
    Performs echo of an of the argument comment
    """
    def prepare_run(self,info,log):
        """
        See interface
        """
        try:
            comment = info[self.COMMENT]
            prefix = info[self.PREFIX]
        except:
            log.fatal('did not find one of the keys [%s]' % (self.COMMENT,self.PREFIX))
            return ''   
        return ('%s "%s"' % (prefix,comment),info)
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, self.COMMENT, 'Descriptive sentence')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the Echo executable')
        return args_handler
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
        if run_code != 0:
            exit_code = run_code
        else:
            out_stream.seek(0)
            out = out_stream.read()
            if len(out) == 0:
                log.error('The output stream did not contain any value. check if key [COMMENT] was set')
                exit_code = 1
            else:
                exit_code = 0
        return (exit_code,info)       
