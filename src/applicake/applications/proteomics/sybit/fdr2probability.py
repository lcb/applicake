'''
Created on Jun 18, 2012

@author: quandtan
'''

import os
import sys
import tabular as tb
import time
from applicake.framework.interfaces import IApplication
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
        return Fdr2ProbabilityTemplate()

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        key = 'PEPCSV'
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
        command = '%s %s' % (prefix,mod_template)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        args_handler.add_app_args(log, self.PEPCSV, 'CSV file originated from a file in pepXML format.')
        args_handler.add_app_args(log, self.DECOY_STRING, 'Prefix to indicate decoy entries in a Protein sequence database.')
        args_handler.add_app_args(log, self.FDR, 'FDR cutoff value that has to be matched')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        out_stream.seek(0)
        out = out_stream.read()
        info['PROBABILITY']= out.rstrip('\r\n')
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
        template = """-IPROPHET -DECOY=$DECOY_STRING -OUT=$PEPCSV -FDR=$FDR $ORGPEPCSV
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
    
    
class Fdr2ProbabilityPython(IApplication):
    # version of the same tool developed as fdr2probabilitydb.py in 0.11 of applicake
    '''
    Stand-alone python version of the Fdr2probability tool including more options to control the calculation.
    
    Added features:
    - minimal reported cutoff is 0.001 to cut off the mainly false positives for a probability of 0.
    - choice of the fdr level  
    '''
    def _get_probability(self,info, log,fdr_col,prob_col):
        # this is the minimal probability value that is returned.
        prob = None       
        data_cutoff = self._data[self._data[fdr_col]<=info[self.FDR]]
        num = len(data_cutoff)
        if num < info[self.NUM_LIMIT] :
            log.error('number of PSMs [%s] matching the probability cutoff [%s][%s] is below the threshold of [%s]' % (num,prob_col,
                                                                                                                       info[self.FDR],
                                                                                                                       info[self.NUM_LIMIT]))
            sys.exit(1)  
        else:
            log.debug('number of PSMs [%s] matching the probability [%s] with FDR cutoff [%s]' % (num,prob_col,info[self.FDR]))
        # need to sort by fdr_col and prob_col. otherwise the num of peps differ for the the fdr-cutoff and the prob-cutoff 
        data_cutoff.sort(order=[prob_col])
        prob = data_cutoff[prob_col][0]
        if prob < info[self.MIN_PROB]: 
            log.debug('probability [%s] is below the cutoff limit [%s]. therefore cutoff limit is applied.' % (prob,info[self.MIN_PROB]))
            prob = info[self.MIN_PROB]        
        else:
            log.debug('probability [%s] matches FDR [%s].' % (prob,data_cutoff[fdr_col][0]))        
        log.debug('num of peptides >= probability[%s] [%s]' % (prob,len(data_cutoff[data_cutoff[prob_col]>=prob]))) 
        return prob               

    def _calc_fdr_psm(self,info, log,dict):
        for k in dict.keys():
            self._data.sort(order=[dict[k]])
            proteins = self._data['protein']
            fdr_vals = []
            t = 0
            f = 0  
            fdr_val = None      
            # data have to be reversed because the previous sorting is low -> high
            # we need however high ->
            for e in proteins[::-1]:
                if info[self.DECOY_STRING] in e: f +=1
                else: t +=1
                fdr_val = float(f) / (float(t) + float(f))
                fdr_vals.append(fdr_val)
            # add re-reversed values that the order matches again what is in the data object
            self._data = self._data.addcols([fdr_vals[::-1]],names=[k]) 
            log.debug('finished calculating fdr for [%s]' % k)                              
                
    def _cal_fdr_peptide(self,info,log,dict):            
        for k in dict.keys():      
            self._data.sort(order=[dict[k]])
#            data = self._data[['protein','peptide']]
            proteins = self._data['protein']
            proteins = proteins[::-1]
            peptides = self._data['peptide']
            peptides = peptides[::-1]
            mod_peptides = self._data['modified_peptide']
            mod_peptides = mod_peptides[::-1]
            
            peptides_nomods_noD = [e['peptide'] for e in self._data[['protein','peptide']] if 'DECOY_' not in e['protein']]
            peptides_mods_noD = [e['modified_peptide'] for e in self._data[['protein','modified_peptide']] if 'DECOY_' not in e['protein']] 
            all_peptides_noD = reduce(lambda x, y: x+y, [peptides_nomods_noD + peptides_mods_noD])
            log.debug(len(all_peptides_noD))
            uniq_peptides_noD = list(set(all_peptides_noD))
            uniq_peptides_noD.remove('NA')
            log.debug(len(uniq_peptides_noD))
            found_pep_ions = []
            log.debug('finished data')
            fdr_vals = []
            t = 0
            f = 0  
            fdr_val = None      
            
            log.debug('finished uniq_peptides') 
            # data have to be reversed because the previous sorting is low -> high
            # we need however high ->
            counter = 0
            chunk = 1000
            tic = time.clock()
            for i,protein in enumerate(proteins):
                if info[self.DECOY_STRING] in protein: 
                    f +=1
                    fdr_val = float(f) / (float(t) + float(f))
                else:
                    ion = None
                    if mod_peptides[i] == 'NA':
                        ion = peptides[i]
                    else:
                        ion = mod_peptides[i]
                    if ion not in  found_pep_ions:
                        found_pep_ions.append(ion)               
                        t +=1
                        fdr_val = float(f) / (float(t) + float(f))                   
                fdr_vals.append(fdr_val)
                counter +=1
                if counter == chunk:
                    chunk += counter
                    print counter
                    print time.clock() - tic     
            # add re-reversed values that the order matches again what is in the data object
            self._data = self._data.addcols([fdr_vals[::-1]],names=[k]) 
            log.debug(len(found_pep_ions))
            log.debug('finished calculating fdr for [%s]' % k)    
    
    def set_args(self,log,args_handler):    
        """ See super class"""
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files') 
        args_handler.add_app_args(log, self.PEPCSV, 'CSV file originated from a file in pepXML format.')
        args_handler.add_app_args(log, self.DECOY_STRING, 'Prefix to indicate decoy entries in a Protein sequence database.')
        args_handler.add_app_args(log, self.FDR, 'FDR cutoff value that has to be matched')
        args_handler.add_app_args(log, self.PROPHET, 'Prophet type used for the calculation. [IProphet|PeptideProphet]')
        args_handler.add_app_args(log, self.FDR_LEVEL, 'Level used for the calculation: [psm|peptide]')
        args_handler.add_app_args(log, self.NUM_LIMIT, 'Number of matches that have to be non-decoy before the first decoy is found.',type=int)
        args_handler.add_app_args(log, self.MIN_PROB, 'Minimal probability that is reported by the program; even if the actual calculated value is lower.',type=float)
        return args_handler

    def main(self,info,log):
        # setting default values
        if not info.has_key(self.FDR_LEVEL): info[self.FDR_LEVEL] = 'psm'
        if not info.has_key(self.NUM_LIMIT): info[self.NUM_LIMIT] = 100
        if not info.has_key(self.MIN_PROB): info[self.MIN_PROB] = 0.001
         
        self._input_filename = info[self.PEPCSV]
        fn = os.path.dirname(info[self.WORKDIR]) + '.csv'
        self._output_filename = os.path.join(info[self.WORKDIR],fn) 
        info[self.PEPCSV] = self._output_filename        
        log.debug('read [%s]' % self._input_filename)
        self._data = tb.tabarray(SVfile=self._input_filename)
        peptides = self._data['peptide'].tolist()
        log.debug('num of peptides [%s]' % len(peptides))      
        uniq_peptides = list(set(peptides)) 
        log.debug('num of unique peptide sequences [%s]' % len(uniq_peptides))                  
        
        dict = {'FDR_PPROPHET':'probability_pp','FDR_IPROPHET':'probability_ip'}
        idx = None
        if info[self.PROPHET] == 'PeptideProphet': idx = 0
        else: idx =1 
        if info[self.FDR_LEVEL] == 'psm':
            self._calc_fdr_psm(info,log,dict)
        else:
            self._cal_fdr_peptide(info,log,dict)   
        self._data.saveSV(self._output_filename,delimiter="\t")                     
        log.debug(self._get_probability(info,log,dict.keys()[idx],dict.values()[idx]))        

    