'''
Created on Jan 11, 2013

@author: wolski
'''

from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils

class SplitDenoise(IWrapper):
    
    def prepare_run(self, info, log):
        filteroptions = "--bin-width=%s --width-RT=%s" % (info['WIDTH'],info['RTWIDTH'])
        command = 'SplitDenoise.sh -t %s -i %s -o %s -r %s -d "%s"' % (info['THREADS'],info['MZXML'],info['WORKDIR'],info['RUNDENOISER'],filteroptions)
        return command, info

    def set_args(self, log, args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, 'THREADS', 'no parallel threads') 
        args_handler.add_app_args(log, 'MZXML', 'mzml files to process.') 
        args_handler.add_app_args(log, 'RUNDENOISER', 'run? True or False')
        args_handler.add_app_args(log, 'WIDTH', 'resolution of instrument in ppm.') 
        args_handler.add_app_args(log, 'RTWIDTH', 'RT Peak width in pixel.')

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        
        for line in out_stream:
            outfiles=line
        info["MZML"] = outfiles.strip().split(", ")
            
        for file in info["MZML"]:
            if not FileUtils.is_valid_file(log, file):
                log.critical('[%s] is not valid' %file)
                return 1,info 
        return 0,info

