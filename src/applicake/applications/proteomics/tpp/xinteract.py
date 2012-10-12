'''
Created on Jun 6, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator
from applicake.framework.templatehandler import BasicTemplateHandler

class Xinteract(IWrapper):
    """
    Wrapper for the TPP-tool xinteract.
    """

    _template_file = ''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.pepxml' % base
        self._template_file = '%s.tpl' % base
        
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'xinteract'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info
    
    def get_template_handler(self):
        """
        Return the template handler
        """
        return XinteractTemplate()    

    def prepare_run(self,info,log):
        """
        See interface.

        - replace list of PEPXMLs with output of the application
        - create command
        """
        key = self.PEPXMLS
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        self._result_file = os.path.join(wd,self._result_file)
        # have to temporarily set a key in info to store the original IDXML
        info['ORG%s'% key] = ','.join(info[key])
        info[key] = self._result_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        # can delete temporary key as it is not longer needed
        del info['ORG%s' % key]
        prefix,info = self.get_prefix(info,log)
        command = '%s %s' % (prefix,mod_template)
        return command,info                
#        wd = info[self.WORKDIR]
#        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
#        self._result_file = os.path.join(wd,self._result_file)
#        old = info[self.PEPXMLS]
#        new = self._result_file
#        log.debug('replace value of [PEPXMLS] [%s] with [%s]' %(old,new))
#        
#        log.debug('get template handler')
#        th = self.get_template_handler()
#        log.debug('modify template')
#        mod_template,info = th.modify_template(info, log)
#        prefix,info = self._get_prefix(info,log)
#        command = '%s -ini %s' % (prefix,self._template_file)
#                     
#        info[self.PEPXMLS] = [new]
#        prefix,info = self.get_prefix(info,log)
#        command = '%s -N%s %s %s' % (prefix,self._result_file,info['XINTERACT_ARGS'],','.join(old))
#        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')  
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')       
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'XINTERACT_ARGS', 'Arguments for xinteract')
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file with target/decoy entries')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.

        Check the following:
        - if decoy hits were found
        - if exit code was non-zero
        - if job is incomplete
        - if file is valid
        - if xml is well-formed
        """
        if 0 != run_code:
            return run_code,info
        out_stream.seek(0)
        err_stream.seek(0)
        if 'No decoys with label' in err_stream.read():
            log.error('found no decoy hits')
            return 1,info                   
        if 'exited with non-zero exit code' in out_stream.read():
            log.error('xinteract did complete with exit code !=0')
            return 1,info
        if 'QUIT - the job is incomplete' in out_stream.read():
            self.log.error('xinteract: job is incomplete')
            return 1,info              
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info
        return 0,info



class XinteractTemplate(BasicTemplateHandler):
    """
    Template handler for xinteract.
    """
    def read_template(self, info, log):
        """
        See super class.
        """
        # Threads is not set by a variable as this does not make sense here
        template = """ -N$PEPXMLS $XINTERACT_ARGS -D$DBASE $ORGPEPXMLS
"""        
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info