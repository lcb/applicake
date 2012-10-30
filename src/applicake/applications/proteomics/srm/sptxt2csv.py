'''
Created on Oct 30, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler

class Sptxt2Csv(IWrapper):
    '''
    Wrapper for sptxt2csv.py from the srmcolider package.
    '''

#    _template_file = ''
#    _result_file = ''
#    _default_prefix = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.csv' % base # result produced by the application

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return Sptxt2CsvTemplate()

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
        info[key] = self._result_file
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        prefix,info = self.get_prefix(info,log)
        root = os.path.splitext(info[self.SPLIB])[0]
        command = '%s --in %s --out %s %s' % (prefix,root,self._result_file,mod_template)
#        /cluster/apps/openms/openswath-testing/mapdiv/scripts/assays/sptxt2csv.py --in /cluster/scratch_
#xl/shareholder/imsb_ra/workflows/812/0/ConsensusLibrary2/ConensusLibrary2 --out step4.tsv --no_filter=NO=FILTER
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        #args_handler.add_app_args(log, '', '')
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


class Sptxt2CsvTemplate(BasicTemplateHandler):
    """
    Template handler for Sptxt2Csv to generate a csv with all transitions (SRM mode).
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """--no_filter=NO=FILTER
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info