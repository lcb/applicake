'''
Created on Jun 18, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler

class Fdr2Probability(IWrapper):
    '''
    Wrapper for sybit tool fdr2probability.
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'fdr2probability'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.result' % base # result produced by the application

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return Fdr2ProbabilityTemplate()

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        key = self._file_type.upper()
        wd = info[self.WORKDIR]        
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._result_file = os.path.join(wd,self._result_file)
        # have to temporarily set a key in info to store the original IDXML
        info['ORG%s'% key] = info[key]
        info[key] = self._result_file
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        # can delete temporary key as it is not longer needed
        del info['ORG%s' % key]          
        prefix,info = self.get_prefix(info,log)
        command = '%s  -OUT=%s -FDR=%s %s %s' % (prefix)
        cmds.append('%s -OUT=%s -FDR=%s %s %s' % (prefixes[1],self._result_filename,peptide_fdr,params[1],csv_filename))
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, 'PEPCSV', 'CSV file originated from a file in pepXML format.')
        args_handler.add_app_args(log, 'DECOY_STRING', 'Prefix to indicate decoy entries in a Protein sequence database.')
        args_handler.add_app_args(log, 'FDR', 'FDR cutoff value that has to be matched')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        return 0,info


class Fdr2ProbabilityTemplate(BasicTemplateHandler):
    """
    Template handler for Fdr2Probability.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """-IPROPHET -DECOY=$DECOY_STRING -OUT=$PEPCSV -FDR=%s $ORGPEPCSV
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info