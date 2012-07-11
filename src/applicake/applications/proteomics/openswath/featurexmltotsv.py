'''
Created on Jul 11, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils

class FeatureXMLToTSV(IWrapper):
    '''
    Wrapper for the FeatureXMLToTSV in OpenSWATH .
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'FeatureXMLToTSV'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.tsv' % base # result produced by the application

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

#    def get_template_handler(self):
#        """
#        See interface
#        """
#        return FeatureXMLToTSVTemplate()

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        key = 'FEATURETSV'
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._result_file = os.path.join(wd,self._result_file)
        info[key] = self._result_file
#        self._template_file = os.path.join(wd,self._template_file)
#        info['TEMPLATE'] = self._template_file
#        log.debug('get template handler')
#        th = self.get_template_handler()
#        log.debug('modify template')
#        mod_template,info = th.modify_template(info, log)
        prefix,info = self.get_prefix(info,log)        
        command = '%s -in %s -tr %s -out %s -short_format' % (prefix,
                                                              info['FEATUREXML'],
                                                              info['TRAML'],
                                                              self._result_file)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
#        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory') 
        args_handler.add_app_args(log, 'FEATUREXML', 'The output featureXML file ')
        args_handler.add_app_args(log, 'TRAML', 'Path to the TraML file.')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info    
        return 0,info


#class FeatureXMLToTSVTemplate(BasicTemplateHandler):
#    """
#    Template handler for FeatureXMLToTSV.
#    """
#
#    def read_template(self, info, log):
#        """
#        See super class.
#        """
#        template = """
#"""
#        log.debug('read template from [%s]' % self.__class__.__name__)
#        return template,info