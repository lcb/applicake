'''
Created on Oct 24, 2012

@author: lorenz
'''
import os

from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class SplitWindows(IWrapper):
    _default_prefix = 'split_mzXML_intoSwath.py'
    
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):

        self.outfolder = info[self.WORKDIR]
        prefix,info = self.get_prefix(info,log)
        command = '%s %s %s %s' % (prefix,info['MZXML'],info['WINDOWS'],self.outfolder)
        return command,info

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.MZXML, 'mzxml to split')
        args_handler.add_app_args(log, 'WINDOWS', 'number of windows to split into', default='32')
        
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        outfiles = []
        for outfile in os.listdir(self.WORKDIR):
            if not str(outfile).endswith('mzXML') or str(outfile).endswith('ms1scan.mzXML'):
                continue
            if not FileUtils.is_valid_file(log, self.outfile):
                log.critical('[%s] is not valid' %self.outfile)
                return 1,info
            if not XmlValidator.is_wellformed(self.outfile):
                log.critical('[%s] is not well formed.' % self.outfile)
                return 1,info 
            outfiles.append(outfile)
            
        info[self.MZXML] = outfiles   
        return 0,info
    