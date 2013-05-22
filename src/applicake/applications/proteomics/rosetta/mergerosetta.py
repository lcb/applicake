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
    
    def prepare_run(self,info,log):
        wd = info[self.WORKDIR]
        mergedfilepath = os.path.join(wd, 'default_merge.out')
        info['ROSETTAMERGEDOUT'] = mergedfilepath
        infiles = ' '.join(info['ROSETTAOUT'])
    
        command = 'combine_silent.default.linuxgccrelease -in::file:silent %s -out:file:silent %s' % (infiles,mergedfilepath)
        return command,info

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'ROSETTAOUT', 'Rosettaout to know which outs to use')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        return run_code,info
