'''
Created on Nov 13, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IApplication
import shutil
from applicake.applications.proteomics.fasta import FastaUtil

class MimicPostprocess(IApplication):
    '''
    Application for postprocessing fasta files created by mimic.
    
    - changing of the header to >DECOY_ for the decoy entries
    - adding the following information to the header of decoy hits: \\DE= Decoy hit
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
        args_handler.add_app_args(log, self.FASTA, 'Sequence file(s) in .fasta format', action ='append') 
        args_handler.add_app_args(log, self.FASTA_DECOY, 'Sequence file(s) with decoy entries in .fasta format', action ='append') 
        return args_handler
 
    def main(self,info,log):
        '''
        
        '''
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        target = info[self.FASTA]
        decoy = info[self.FASTA_DECOY]
        final_fasta = []
        for i,e in enumerate(decoy):
            basename = os.path.basename(e)
            final_fasta.append(os.path.join(wd,basename))
            log.debug('transform decoy fasta [%s]' % decoy[i])
            df = FastaUtil.read(decoy[i], log)
            # add decoy suffix
            df['protein'] = df['protein'].map(lambda x: 'DECOY_%s' % x)
            df['description'] = df['description'].map(lambda x: '%s \\\\DE= decoy hit' % x)
            FastaUtil.write(df, final_fasta[i], log, split_pos=60)
            log.debug('add content of [%s] to [%s]' % (target[i],final_fasta[i]))
            fin = open(target[i],'r+')
            fout = open(final_fasta[i],'a')
            fout.write(fin.read())
            fin.close()
            fout.close()
        info[self.FASTA] = final_fasta
        return 0,info