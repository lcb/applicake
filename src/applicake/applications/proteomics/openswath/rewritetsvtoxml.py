'''
Created on Jul 11, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils

class RewriteTSVToFeatureXML(IWrapper):
    '''
    Wrapper for the OpenSwathRewriteToFeatureXML tool.
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'OpenSwathRewriteToFeatureXML'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.featureXML' % base # result produced by the application

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
        wd = info[self.WORKDIR]
        self._result_file = os.path.join(wd,self._result_file)
        prefix,info = self.get_prefix(info,log)   
        command = '%s -FDR_cutoff 1 -featureXML %s -csv %s -out %s -threads %s' % (prefix,
                                                              info['FEATUREXML'],
                                                              info['MPROPHET_TSV'],
                                                              self._result_file,
		 													  info['THREADS'])
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory') 
        args_handler.add_app_args(log, 'FEATUREXML', 'The output featureXML file ')
        args_handler.add_app_args(log, 'MPROPHET_TSV', 'mprophets allpeakgroups result file')
        args_handler.add_app_args(log, 'THREADS', 'number of threads to use')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info    
        
        info['FEATUREXML'] = self._result_file
        return 0,info
