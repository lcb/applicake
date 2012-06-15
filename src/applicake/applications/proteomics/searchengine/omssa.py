'''
Created on Jun 14, 2012

@author: quandtan
'''

import os
from applicake.applications.proteomics.modifications import ModificationDb
from applicake.applications.proteomics.base import MsMsIdentification
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class Omssa(MsMsIdentification):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(Omssa,self).__init__()
        base = self.__class__.__name__
        self._result_file = '%s.pepXML' % base # result produced by the application
        
    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'omssacl'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return OmssaTemplate()

    def prepare_run(self,info,log):
        """
        See interface.

        - 
        """
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file) 
        info['TEMPLATE'] = self._template_file
        self._result_file = os.path.join(wd,self._result_file) 
        info['PEPXML'] = self._result_file
        log.debug('define modifications')
        info = self.define_mods(info, log)    
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        prefix,info = self._get_prefix(info,log)
        command = "%s %s -fm %s -op %s" %(prefix,mod_template,info['MGF'],self._result_file)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(Omssa, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'MGF', 'Peak list file in mgf format')  
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.

        Check the following:
        -
        """
        exit_code,info = super(Omssa,self).validate_run(info,log, run_code,out_stream, err_stream)
        if 0 != run_code:
            return exit_code,info
        out_stream.seek(0)
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info
        return 0,info


class OmssaTemplate(BasicTemplateHandler):
    """
    Template handler for Omssa.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """-nt $THREADS -d $DBASE -e 0 -v -mf $MISSEDCLEAVAGE -mv $STATIC_MODS $VARIABLE_MODS -he 100000.0 -zcc 1 -ii 0 -te $PRECMASSERR -to $FRAGMASSERR -ht 6 -hm 2 -ir 0 -h1 100 -h2 100 -hl 1
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info