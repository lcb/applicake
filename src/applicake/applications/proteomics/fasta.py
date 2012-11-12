'''
Created on Nov 11, 2012

@author: quandtan
'''

import pandas
import sys
from applicake.utils.stringutils import StringUtils
from applicake.framework.logger import Logger
from StringIO import StringIO
from applicake.utils.fileutils import FileUtils


class FastaReader():
    '''
    Reader for files in FASTA format.
    '''
    
    def read(self,path,log=None):
        '''
        Return data frame with the columns [protein,description,sequence].
        '''
        if log == None:
            log = Logger.create(level='DEBUG',name=StringUtils.get_random(15),stream=StringIO())            
        if not FileUtils.is_valid_file(log, path):
            sys.exit(1)        
        entries = []
        for line in file(path):
            if line.startswith('>'):                 
                header = line[1:].rstrip('\n').split(' ')
                entries.append({
                                'protein':header[0],
                                'description':' '.join(header[1:]),
                                'sequence' : ''
                                })
            else:
                entries[-1]['sequence'] += line.rstrip('\n')            
        log.debug("%d sequences found" % len(entries))
        return pandas.DataFrame(entries)
        