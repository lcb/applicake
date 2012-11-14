'''
Created on Nov 14, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper

class Fasta2Inspect(IWrapper):
    '''
    Wrapper for Prep.py from the InsPecT software package.
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'Prep.py'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.' % base # result produced by the application

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
        key = self.TRIE
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        basename = os.path.basename(info[self.FASTA])
        self._result_file = os.path.join(wd,'%s.trie' % basename)
        info[key] = self._result_file
        prefix,info = self.get_prefix(info,log)
        command = '%s FASTA %s ' % (prefix,info[self.FASTA])
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        args_handler.add_app_args(log, self.FASTA, 'Sequence file in .fasta format')
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