'''
Created on Nov 6, 2012

@author: quandtan
'''

import csv
import operator
import os
import pandas
import sys


from applicake.framework.interfaces import IApplication
from applicake.utils.fileutils import FileUtils
from applicake.applications.proteomics.fasta import FastaReader
from applicake.utils.sequenceutils import SequenceUtils

class TraCsvFilter(IApplication):
    '''
    Create a subset of the original list of transitions based on the applied filters.
    '''  
    
    _result_file = ''
    _delimiter = '\t'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.csv' % base # result produced by the application
        self._default_intensity_criteria = 'PeptideSequence'  

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.TRACSV, 'File in .csv format (tab-delimited) that contains the transitions for SRM.')
        args_handler.add_app_args(log,self.ANNOTATED , 'If set, removes transitions without annotation.',action="store_true",default=False)
        args_handler.add_app_args(log,self.NO_ISOTOPES , 'If set, removes transitions without annotation.',action="store_true",default=False) 
        args_handler.add_app_args(log,self.MASSMODS, 'List of allowed fragment mass modifications. Example: -80,-98 (Phosphorylation)',action="append")
        args_handler.add_app_args(log,self.MASSWIN , 'Allowed mass error. Example: 0.025 for -0.025/+0.025',type=float)   
        args_handler.add_app_args(log,self.PRECMASS_RANGE , 'Allowed mass range for precursor mass of each transition. Example: [200-1200]')
        args_handler.add_app_args(log,self.NO_HIGHPRODMZ , 'If set, removes transitions for which the ProductMz > PrecursorMz',action="store_true",default=False)
        args_handler.add_app_args(log,'DBASE' , 'Sequence database file with target/decoy entries.')
        args_handler.add_app_args(log,self.NO_DECOY , 'If set, decoy entries are not checked',action="store_true",default=False)
        args_handler.add_app_args(log, self.N_MOST_INTENSE, 'Number of n most intense [peptides[transition groups per protein that should be included into the transition list. Example[3]',type=int)
        args_handler.add_app_args(log, self.INTENSITY_CRITERIA, 'Intensity criteria [default:PeptideSequence]',
                                  choices=['PeptideSequence','transition_group_id'])          
        return args_handler
 
    def main(self,info,log):
        df  = self._read_dataframe(info, log)
        len_df = len(df)
        # some annotations are surrounded by '[]'. these parentheses have to be removed.
        df['Annotation'] = df['Annotation'].map(lambda x : x.replace("[",'').replace(']',''))
        # non-annotated transitions (marked by '?') are not selected if filter is active
        if info[self.ANNOTATED]: 
            df = df[df['Annotation'] != '?']
        # isotopic annotations are removed if filter is active.
        if info[self.NO_ISOTOPES]:
            # if there are multiple annotations (e.g. 'y5-35^2/0.04,y5-36^2i/0.53,a7^3/-0.28'),
            #  the annotation containing the isotope is removed from list
            df['Annotation'] = df['Annotation'].map(lambda x : ','.join([e for e in x.split(',') if not 'i' in e]) )
            # the previous line produces empty annotations if there is only a single annotation 
            #  which is also an isotope. they have to be removed.
            df = df[df['Annotation'] != '']
        # delete annotations that contain modifs other than the specified if filter is active
        if info.has_key(self.MASSMODS): 
            # apply filter              
            df['Annotation'] = df['Annotation'].map(lambda x : self._filter_annotation_modif(info,x) )
            # remove potential empty annotations
            df = df[df['Annotation'] != '']
        # annotations with too large mass shift are removed if filter is active.
        if info.has_key(self.MASSWIN):
            # first split multiple annotations, then extract mass error for each annotation
            # remove annotations if the absolute value is larger than the defined limit
            df['Annotation'] = df['Annotation'].map(lambda x : ','.join([e for e in x.split(',') if abs(float(e.split('/')[1])) <= info[self.MASSWIN]]))
            # remove potentially created empty annotations
            df = df[df['Annotation'] != '']
        # filters for the precursor mass if filter is active
        if info.has_key(self.PRECMASS_RANGE):
            min = info[self.PRECMASS_RANGE].split('-')[0]
            max = info[self.PRECMASS_RANGE].split('-')[1]
            df = df[(df['PrecursorMz']>=min) &(df['PrecursorMz']<=max)]
        if info[self.NO_HIGHPRODMZ]:
            df = df[df['PrecursorMz']>= df['ProductMz']]
        if info.has_key('DBASE'):
            df_fas = FastaReader().read(info['DBASE'],log)
            if info[self.NO_DECOY]:
                df_fas = df_fas[df_fas['protein'].map(lambda x : 'DECOY' in x)]
            seq_list = df_fas['sequence'].to_dict().items()
            df[df['PeptideSequence'].map(lambda x: len(SequenceUtils.findall(seq_list,lambda y: x in y)) > 1)]
        # filter for the N-most intense [peptides, transition groups] if active    
        if info.has_key(self.N_MOST_INTENSE):
            # set default if not defined by the user
            if not info.has_key(self.INTENSITY_CRITERIA):
                info[self.INTENSITY_CRITERIA] = self._default_intensity_criteria
                log.warning('no value found for key [%s]. set it to [%s]'% (self.N_MOST_INTENSE,self._default_intensity_criteria))                
            df = self._filter_intensity(info,log,df)
        log.debug('selected [%s] out of [%s] transitions' % (len(df),len_df))        
        self._write_dataframe(info, log, df)  
        return 0,info  

    def _filter_annotation_modif(self,info, annotation):
            new_annotation = []
            # look for multiple annotations
            for annot in annotation.split(','):     
                # check if annotation contains a modif                
                if '+' in annot or '-' in annot: 
                    # if modif has not beed defined, it is not selected
                    for e in info[self.MASSMODS]:
                        if e in annot: 
                            new_annotation.append(annot)
                else:
                    new_annotation.append(annot)
            return ','.join(new_annotation)         


    def _filter_intensity(self,info,log,df):
        ''' 
        Filter for the most n intense criteria.
        '''
        pn = ''
        ps = []
        limit = info[self.N_MOST_INTENSE]
        num_transitions = 0 
        self._selected_data = []  
        df = df.sort_index(by=['ProteinName','LibraryIntensity'])            
        for idx,row in df.iterrows():
            #check if row contains a new protein name
            if pn == row['ProteinName']:
                # transition is not selected if not and the limit of n most intense transitions is reached.
                if num_transitions >= limit:
                    continue
                # transition is not selected if the peptide sequence has been already selected before.    
                elif row[info[self.INTENSITY_CRITERIA]] in ps:
                    continue
                else:
                    num_transitions +=1
                    ps.append(row[info[self.INTENSITY_CRITERIA]])
                    self._selected_data.append(row)
            else:
                pn = row['ProteinName']
                ps = [row[info[self.INTENSITY_CRITERIA]]]
                num_transitions = 1 
                self._selected_data.append(row) 
        return pandas.DataFrame(self._selected_data)    
    
    def _read_dataframe(self,info,log):
        '''
        Return a data frame. 
        '''
        f = info[self.TRACSV]
        if not FileUtils.is_valid_file(log, f):
            log.fatal('file [%s] is not valid' % f)
            sys.exit(1)
        df = pandas.read_table(f)
        log.debug('read data from [%s]' % info[self.TRACSV])
        return df
        
    def _write_dataframe(self,info,log,dataframe):
        wd = info[self.WORKDIR]
        self._result_file = os.path.join(wd,self._result_file)
        info[self.TRACSV] = self._result_file
        dataframe.to_csv(info[self.TRACSV],sep='\t')
        log.debug('wrote results to [%s]' % self._result_file)       
