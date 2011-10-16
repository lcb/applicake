#!/usr/bin/env python
'''
Created on Feb 21, 2011

@author: quandtan
'''
#
import argparse,os,sys,fileinput,logging,glob,csv
import tabular as tb
import time
from applicake.app import Application
        #
class Fdr2Probability(Application):
    '''
    doc
    '''
    #
    #
    def __init__(self, use_filesystem=True,log_level=logging.DEBUG,name=None,log_console=True):
        super(Fdr2Probability, self).__init__(use_filesystem=use_filesystem,log_level=log_level,name=name,log_console=log_console)
    #
    def _get_parsed_args(self,args):
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('-i','--input',required=True, nargs=1,action="store", dest="input_filename",type=str,help="input file")
        parser.add_argument('-o','--output',required=True,nargs=1, action="store", dest="output_filename",type=str,help="output file")
        parser.add_argument('-p','--prophet',required=False, nargs=1, default=['ip'],action="store", dest="prophet",type=str,help="pepxml prophet type")
        parser.add_argument('-d','--decoy',required=False,nargs=1,default=['DECOY_'], action="store", dest="decoy",type=str,help="decoy prefix")
        parser.add_argument('-l','--level',required=False,nargs=1,default=['psm'], action="store", dest="level",type=str,help="fdr level")
        parser.add_argument('-c','--cutoff',required=False,nargs=1,default=[0.01], action="store", dest="cutoff",type=float,help="fdr cutoff")
        parser.add_argument('-n','--name',required=False,default=[self.name],nargs=1, action="store", dest="name",type=str,help="identifier used in the process")
        a = parser.parse_args(args)
        if type(a.name) is list:
            a.name = a.name[0]        
        return {
                'input_filename':a.input_filename[0],
                'output_filename':a.output_filename[0],
                'prophet':a.prophet[0],
                'decoy':a.decoy[0],
                'level':a.level[0],
                'cutoff':a.cutoff[0],
                'name':a.name[0]}
    #
    def _get_probability(self,fdr_col,prob_col):
        cutoff_limit = 0.001
        num_limit = 100
        prob = None       
        data_cutoff = self._data[self._data[fdr_col]<=self._cutoff]
        num = len(data_cutoff)
        if num < num_limit :
            self.log.error('number of PSMs [%s] matching the probability cutoff [%s][%s] is below the threshold of [%s]' % (num,prob_col,self._cutoff,num_limit))
            sys.exit(1)  
        else:
            self.log.debug('number of PSMs [%s] matching the probability [%s] with FDR cutoff [%s]' % (num,prob_col,self._cutoff))
        # need to sort by fdr_col and prob_col. otherwise the num of peps differ for the the fdr-cutoff and the prob-cutoff 
        data_cutoff.sort(order=[prob_col])
        prob = data_cutoff[prob_col][0]
        if prob < cutoff_limit: 
            self.log.debug('probability [%s] is below the cutoff limit [%s]. therefore cutoff limit is applied.' % (prob,cutoff_limit))
            prob = cutoff_limit        
        else:
            self.log.debug('probability [%s] matches FDR [%s].' % (prob,data_cutoff[fdr_col][0]))        
        self.log.debug('num of peptides >= probability[%s] [%s]' % (prob,len(data_cutoff[data_cutoff[prob_col]>=prob]))) 
        return prob               
    #
    def _preprocessing(self):
        self.log.debug('read [%s]' % self._input_filename)
        self._data = tb.tabarray(SVfile=self._input_filename)
        peptides = self._data['peptide'].tolist()
        self.log.debug('num of peptides [%s]' % len(peptides))      
        uniq_peptides = list(set(peptides)) 
        self.log.debug('num of unique peptide sequences [%s]' % len(uniq_peptides))        
        #
    def _calc_fdr_psm(self, dict):
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
                if self._decoy in e: f +=1
                else: t +=1
                fdr_val = float(f) / (float(t) + float(f))
                fdr_vals.append(fdr_val)
            # add re-reversed values that the order matches again what is in the data object
            self._data = self._data.addcols([fdr_vals[::-1]],names=[k]) 
            self.log.debug('finished calculating fdr for [%s]' % k)                              
                
    def _cal_fdr_peptide(self,dict):            
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
            print len(all_peptides_noD)
            uniq_peptides_noD = list(set(all_peptides_noD))
            uniq_peptides_noD.remove('NA')
            print len(uniq_peptides_noD)
            
            found_pep_ions = []
            print 'finished data'
            fdr_vals = []
            t = 0
            f = 0  
            fdr_val = None      
            
            print 'finished uniq_peptides' 
            # data have to be reversed because the previous sorting is low -> high
            # we need however high ->
            counter = 0
            chunk = 1000
            tic = time.clock()
            for i,protein in enumerate(proteins):
                if self._decoy in protein: 
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
            print len(found_pep_ions)
            self.log.debug('finished calculating fdr for [%s]' % k)             
            #                                    
    def _run(self,command=None):        
        dict = {'FDR_PPROPHET':'probability_pp','FDR_IPROPHET':'probability_ip'}
        idx = None
        if self._prophet == 'pp': idx = 0
        else: idx =1 
        if self._level == 'psm':
            self._calc_fdr_psm(dict)
        else:
            self._cal_fdr_peptide(dict)  
        self._data.saveSV(self._output_filename,delimiter='t')                    
        print self._get_probability(dict.keys()[idx],dict.values()[idx])
        #
    def _validate_parsed_args(self,dict):           
        self._input_filename = dict['input_filename']
        self._output_filename = dict['output_filename']
        self._prophet = dict['prophet']
        self._decoy = dict['decoy']
        self._level = dict['level']
        self._cutoff = dict['cutoff']
        self.name = dict['name']
        self.log.debug("input file [%s]" % os.path.abspath(self._input_filename))
        if not os.path.exists(self._input_filename):
            self.log.fatal('file [%s] does not exist' % self._input_filename)
            sys.exit(1)
        keywords = ['ip','pp']
        if not any( [k == self._prophet for k in keywords] ):
            self.log.fatal("the value of argument 'prophet' was [%s] and not one of [%s]" % (self._prophet,keywords))
            sys.exit(1) 
        keywords = ['psm','peptide']
        if not any( [k == self._level for k in keywords] ):
            self.log.fatal("the value of argument 'prophet' was [%s] and not one of [%s]" % (self._level,keywords))
            sys.exit(1)             
        if not 0 <= self._cutoff <= 1:
            self.log.fatal("the value of argument 'fdr' was [%s] and not between 0 and 1" % self._cutoff)
            sys.exit(1)                 
    #       
    def _validate_run(self,run_code=None):                   
        return 0  
    #   
if '__main__'==__name__:       
    a = Fdr2Probability(use_filesystem=False)
    exit_code = a(sys.argv)
#    print(exit_code)
    sys.exit(exit_code)      
    