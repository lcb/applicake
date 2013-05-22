'''
Created on Jul 11, 2012

@author: loblum
'''

from applicake.framework.interfaces import IWrapper

class Extractrosetta(IWrapper):
    '''
    Extract rosetta dataset tgz to flat folder WORKDIR
    '''
    def prepare_run(self,info,log):
        wd = info[self.WORKDIR]
        info['ROSETTAINPUTDIR'] = wd
        archivepath = None
        for dssout in info[self.DSSOUTPUT]:
            if dssout.endswith('tgz'):
                archivepath = dssout  
        #goto WD extract tar, junk subdirectory  
        command = 'cd %s && tar -xf %s --strip 1' % (wd,archivepath)
        return command,info

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.DSSOUTPUT, 'Dssout to know which tgz to use')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        return run_code,info
