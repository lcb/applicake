'''
Created on Nov 20, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IApplication

class FastaMetaData(IApplication):
    '''
    Application that creates a meta-data file for each fasta file.
    '''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.result' % base # result produced by the application

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')
        args_handler.add_app_args(log, self.FASTA, 'Sequence file(s) in .fasta format', action ='append')
        return args_handler
 
    def main(self,info,log):
        '''
        
        '''
        wd = info[self.WORKDIR]
        info[self.FASTADIR] = wd
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        for fasta in info[self.FASTA]:
            basename = os.path.basename(fasta)            
            dest = os.path.join(wd,basename)
            root = os.path.splitext(dest)[0]
            os.symlink(fasta, dest)
            meta_file = open('%s.meta' % root,'w+')
            # has to / can be filled with information
            meta_file.write('')
            meta_file.close()
        return 0,info