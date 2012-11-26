'''
Created on Jun 18, 2012

@author: loblum
'''

import os
import sys
import shutil
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class PeptideProphet(IWrapper):
    '''
    Wrapper for TPP-tool PepProphet.
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'PeptideProphetParser'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.pep.xml' % base # result produced by the application

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        #original to copy
        if len(info[self.PEPXMLS]) >1:
            log.fatal('found > 1 pepxml files [%s].' % info[self.PEPXMLS])
            sys.exit(1)
        copyxml =  info[self.PEPXMLS][0]
        #target path
        wd = info[self.WORKDIR]
        self._result_file = os.path.join(wd,self._result_file)
        shutil.copy(copyxml, self._result_file)
        info[self.PEPXMLS] = [self._result_file]
                
        #template       
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        mod_template,info = PeptideProphetTemplate().modify_template(info, log)
         
        prefix,info = self.get_prefix(info,log)
        command = '%s %s %s' % (prefix,self._result_file,mod_template)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.DECOY_STRING, 'String used to annotate decoys')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
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


class PeptideProphetTemplate(BasicTemplateHandler):
    """
    Template handler for ProteinProphet.
    
    Calculations are done on iprophet score.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """DECOY=$%s DECOYPROBS MINPROB=0 PI ACCMASS LEAVE NONPARAM Pd 
""" % (self.DECOY_STRING)
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info