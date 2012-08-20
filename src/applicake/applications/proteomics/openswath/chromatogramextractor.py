'''
Created on Jul 11, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class ChromatogramExtractor(IWrapper):
    '''
    Wrapper for the ChromatogramExtractor of OpenSWATH.
    '''

    _template_file = ''
    _default_prefix = 'ChromatogramExtractor'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._file_suffix = '_rtnorm.chrom.mzML'

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
        key = 'RTNORM_CHROM_MZML' #self._file_type.upper()
        infile = info['MZMLGZ']
        self.outfile = infile.replace("mzML.gz",self._file_suffix)
        info[key] = self.outfile
        prefix,info = self.get_prefix(info,log)
        command = '%s -in %s -tr %s -min_upper_edge_dist %s -threads %s -is_swath -out %s' % (prefix,
                                                                                              info['MZMLGZ'],
                                                                                              info['IRTTRAML'],
                                                                                              info['MIN_UPPER_EDGE_DIST'],
                                                                                              info['THREADS'],
                                                                                              outfile)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.

        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory') 
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.') 
        args_handler.add_app_args(log, 'IRTTRAML', 'Path to the TraML file.')
        args_handler.add_app_args(log, 'MZMLGZ', 'Path to the gzipped mzML files.')
        args_handler.add_app_args(log, 'MIN_UPPER_EDGE_DIST', '')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        if not FileUtils.is_valid_file(log, self.outfile):
            log.critical('[%s] is not valid' %self.outfile)
            return 1,info
        if not XmlValidator.is_wellformed(self.outfile):
            log.critical('[%s] is not well formed.' % self.outfile)
            return 1,info    
        return 0,info