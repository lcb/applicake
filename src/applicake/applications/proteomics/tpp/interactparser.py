'''
Created on Jun 25, 2012

@author: loblum
'''

import os
from applicake.applications.proteomics.base import SearchEngine
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class InteractParser(SearchEngine):
    '''
    Wrapper for the TPP-tool RefreshParser .
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'InteractParser'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.pep.xml' % base # result produced by the application
    
    def get_template_handler(self):
        """
        See interface
        """
        return InteractParserTemplate()
    
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info
    
    def prepare_run(self,info,log):
        #template
        wd = info[self.WORKDIR]
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        #don't modify the original info with enzyme, use copy
        infocopy = info.copy()
        infocopy = self.define_enzyme(infocopy, log)  
        mod_template,infocopy = self.get_template_handler().modify_template(infocopy, log)
        
        #input file(s)
        key = 'PEPXMLS'
        origpepxmls = ' '.join(info['PEPXMLS']) 
        
        #output comes instead of input
        self._result_file = os.path.join(wd,self._result_file)
        info[key] = [self._result_file]
        
        prefix,info = self.get_prefix(info,log)
        command = '%s %s %s %s' % (prefix,self._result_file,origpepxmls,mod_template)
        return command,info  

    def set_args(self,log,args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        args_handler.add_app_args(log, 'PEPXMLS', 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'ENZYME', 'Enzyme used for digest')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info             
        return 0,info


class InteractParserTemplate(BasicTemplateHandler):

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """-L7 -E$ENZYME -C
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
