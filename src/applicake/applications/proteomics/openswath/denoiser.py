'''
Created on Jan 11, 2013

@author: wolski
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class Denoiser(IWrapper):
    '''
    Wrapper for the ChromatogramExtractor of OpenSWATH.
    '''

   
    _default_prefix = 'filter'

    def __init__(self):
        pass

    def get_prefix(self, info, log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX, info[self.PREFIX]))
        return info[self.PREFIX], info

    def helper(self, key):
    	return key.replace('.gz', 'filtered.mzML')


    def prepare_run(self, info, log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        self.outfile = os.path.join(info[self.WORKDIR], 'ChromatogramExtractor.chrom.mzML')
        info['FILTERED_MZML'] = self.outfile
        prefix, info = self.get_prefix(info, log)
        
        inputFile = ''
        outputFiles = []
        #copyCommand = ''
        
        for key in info['MZML']:
            inputFile += ' --in ' + key
            outputFiles.append(self.helper(key))
            #copyCommand += 'cp %s %s && ' % (key, self.helper(key))
            #copyCommand += ' echo'
                
        command = '%s %s --bin-width=%s --width-RT=%s' % (prefix, inputFile,info['WIDTH'],info['RTWIDTH'])

        info['MZML'] = outputFiles
        return command, info

    def set_args(self, log, args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, 'MZML', 'mzml files to process.') 
        args_handler.add_app_args(log, 'WIDTH', 'resolution of instrument in ppm.') 
        args_handler.add_app_args(log, 'RTWIDTH', 'RT Peak width in pixel.')
        
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code, info
    # out_stream.seek(0)
    # err_stream.seek(0)
        # if not FileUtils.is_valid_file(log, self.outfile):
        #    log.critical('[%s] is not valid' %self.outfile)
        #    return 1,info
        # if not XmlValidator.is_wellformed(self.outfile):
        #    log.critical('[%s] is not well formed.' % self.outfile)
        #    return 1,info    
        return 0, info

