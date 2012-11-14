'''
Created on Nov 11, 2012

@author: quandtan
'''


import pandas


class FastaUtil():
    '''
    Utility class for dealing with fasta files.
    '''

    @staticmethod
    def filter(dataframe, str):
        '''
        Filters all sequence entries in the data frame.
        A subset of the data frame is return where each entry's description contains the search string.
        '''
        return dataframe[dataframe['description'].str.contains(str)]
        
    
    @staticmethod
    def read(path,log):
        '''
        Read a fasta file and returns a data frame with the columns [protein,description,sequence].
        '''        
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
     

    @staticmethod
    def write(dataframe,path,log,split_pos=None):
        '''
        Write a data frame containing sequence entries to a file.
        '''
        f = open(path,'w+')
        for row in dataframe.iterrows():
            prot = row[1]['protein']
            desc = row[1]['description']
            seq = row[1]['sequence']
            if split_pos is not None:
                seq = '\n'.join([seq[i:i+split_pos] for i in range(0, len(seq), split_pos)])
            f.write('>%s %s\n%s\n' % (prot,desc,seq))
        log.debug('wrote results to [%s]' % path) 
         
        