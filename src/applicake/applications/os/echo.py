#!/usr/bin/env python
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
    def prepare_run(self,info,log):
        """
        See interface
        """
        try:
            comment = info[self.comment_key]
            prefix = info[self.prefix_key]
        except:
            log.fatal('did not find one of the keys [%s]' % (self.comment_key,self.prefix_key))
            return ''   
        return ('%s "%s"' % (prefix,comment),info)
    
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
