'''
Created on Jul 11, 2012

@author: loblum
'''
import os
from applicake.framework.interfaces import IWrapper

class Mergerosetta(IWrapper):
    '''
    Merge rosetta outs
    '''
    _default_prefix = 'combine_silent.default.linuxgccrelease'
    
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        """
        prefix,info = self.get_prefix(info,log)        
        wd = info[self.WORKDIR]
        mergedfilepath = os.path.join(wd, 'default_merge.out')
        info['ROSETTAMERGEDOUT'] = mergedfilepath
        infiles = ' '.join(info['ROSETTAOUT'])
    
        command = '%s -in::file:silent %s -out:file:silent %s' % (prefix,infiles,mergedfilepath)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'ROSETTAOUT', 'Rosettaout to know which outs to use')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """ 
        return run_code,info
