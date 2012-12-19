'''
Created on Oct 24, 2012

@author: lorenz
'''
import os, re

from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class SplitWindowsConvertZip(IWrapper):
    _default_prefix = 'split_mzXML_into_SWATHmzMLgz.sh'
    
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):

        self.outfolder = info[self.WORKDIR]
        prefix,info = self.get_prefix(info,log)
        command = '%s %s %s noms1map' % (prefix,info[self.MZXML],info['WINDOWS'],self.outfolder)
        del info[self.MZXML]
        return command,info

    def set_args(self,log,args_handler):
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
        for outfile in os.listdir(info[self.WORKDIR]):
            outfile = os.path.join(info[self.WORKDIR],outfile)
            if str(outfile).endswith('mzXML'):
                if not FileUtils.is_valid_file(log, outfile):
                    log.critical('[%s] is not valid' %outfile)
                    return 1,info
                outfiles.append(outfile)
        
        #sort outfiles numerically, http://code.activestate.com/recipes/135435-sort-a-string-using-numeric-order/
        def stringSplitByNumbers(x):
            r = re.compile('(\d+)')
            l = r.split(x)
            return [int(y) if y.isdigit() else y for y in l]
        outfiles = sorted(outfiles, key=stringSplitByNumbers)
            
        info[self.MZML] = outfiles   
        return 0,info
    