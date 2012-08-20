'''
Created on Aug 14, 2012

@author: blum, wolski
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class FileMerger(IWrapper):
    '''
    Wrapper for the ChromatogramExtractor of OpenSWATH.
    '''
    _template_file = ''
    _result_file = 'FileMerger.rtnorm.chrom.mzML'
    _default_prefix = 'FileMerger'


    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        wd = info['RTNORM_CHROM_MZML']
        wd = os.path.dirname(wd)
        infiles = os.path.join(wd, "*._rtnorm.chrom.mzML")
        
     
        self._result_file = os.path.join(wd,self._result_file)
        info["OUTCHROMMZML"] = self._result_file
        prefix,info = self.get_prefix(info,log)
        command = '%s -in %s -out %s' % (prefix, infiles, info['OUTCHROMMZML'])
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory') 
        args_handler.add_app_args(log, 'RTNORM_CHROM_MZML', 'chrom.mzml files to merge.') 
        
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        if not FileUtils.is_valid_file(log, info['OUTCHROMMZML']):
            log.critical('[%s] is not valid' %info['OUTCHROMMZML'])
            return 1,info
        if not XmlValidator.is_wellformed(info['OUTCHROMMZML']):
            log.critical('[%s] is not well formed.' %info['OUTCHROMMZML'])
            return 1,info    
        return 0,info