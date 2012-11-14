'''
Created on Nov 13, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IApplication
from applicake.applications.proteomics.fasta import FastaUtil

class FastaFilter(IApplication):
    '''
    Filters a fasta file to create subsets based on specific search strings
    '''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.fasta' % base # result produced by the application

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')
        args_handler.add_app_args(log, self.FASTA, 'Sequence file in .fasta format')
        args_handler.add_app_args(log, self.FASTA_SUBSETS, 'List of filter strings used to create subsets.',action='append')
        return args_handler
 
    def main(self,info,log):
        '''
        
        '''        
        df_fasta = FastaUtil.read(info[self.FASTA], log)
        info[self.FASTA] = []
        wd = info[self.WORKDIR]
        for str in info[self.FASTA_SUBSETS]:
            path = os.path.join(wd,'%s.fasta' % str)
            log.debug('create subset for [%s]' % str)
            df_subset = FastaUtil.filter(df_fasta, str)
            log.debug('write subset to file [%s]' % path)
            FastaUtil.write(df_subset, path, log,split_pos=60)
            info[self.FASTA].append(path)       
        return 0,info