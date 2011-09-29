#!/usr/bin/env python
'''
Created on Feb 21, 2011

@author: quandtan
'''
#
import argparse,os,sys,fileinput,logging,glob,sqlite3,csv
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
        self.sep = "\t"
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
        self._sql.execute('select count(%s) from %s where %s < %s' % (prob_col,self._tbl_name,fdr_col,self._cutoff) )
        num = self._sql.fetchone()[0]
        if num < num_limit :
            self.log.error('number of PSMs [%s] matching the probability cutoff [%s][%s] is below the threshold of [%s]' % (num,prob_col,self._cutoff,num))
            sys.exit(1)  
        else:
            self.log.debug('number of PSMs [%s] matching the probability cutoff [%s][%s]' % (num,prob_col,self._cutoff))                           
        try:
            self._sql.execute('select %s from %s where %s < %s order by %s desc limit 1 ' % (prob_col,self._tbl_name,fdr_col,self._cutoff,fdr_col) )            
            prob = self._sql.fetchone()[0]
        except:
            self.log.error('could not fetch a probability value.')
            sys.exit(1)
        if prob < cutoff_limit: 
            self.log.debug('probabiliity [%s] is below the cutoff value [%s]. therefore cutoff value is returned.' % (prob,cutoff_limit))
            prob = cutoff_limit
        return prob               
    #
    def _preprocessing(self):
        self.log.debug('read [%s]' % self._input_filename)
        reader = csv.DictReader(open(self._input_filename), delimiter='\t')
        header = reader.fieldnames
        new_col_names = ['FDR_PPROPHET','FDR_IPROPHET']      
        self.log.debug('init db')
        tbl_name = 'pepcsv'
        con = sqlite3.connect(':memory:') 
#        con = sqlite3.connect('fdr2probability.db') 
        # If you want autocommit mode, then set isolation_level to None
        con.isolation_level = None
        sql = con.cursor()
        cols =["%s int primary key"% header[0]]
        cols +=["%s varchar(100) not null"% header[1]]
        cols +=["%s double not null"% header[2]]
        cols +=["%s int(11) not null"% header[3]]
        cols +=["%s varchar(50) not null"% header[4]]
        cols +=["%s varchar(100) not null"% header[5]]
        cols +=["%s varchar(255) not null"% header[6]]
        cols +=["%s char(1) not null"% header[7]]
        cols +=["%s char(1) not null"% header[8]]
        cols +=["%s varchar(150) not null"% header[9]]
        cols +=["%s double not null"% header[10]]
        cols +=["%s double not null"% header[11]]
        cols +=["%s int(11) not null"% header[12]]
        cols +=["%s double not null"% header[13]]
        cols +=["%s double not null"% header[14]]   
        cols +=["%s double"% new_col_names[0]]
        cols +=["%s double"% new_col_names[1]]         
        sql.execute("drop table if exists %s" % tbl_name)
        sql.execute('create table if not exists %s (%s)' % (tbl_name,','.join(cols)))            
        for i in reader:
            keys = '"' + '","'.join(i.keys()) + '"'
            values = '"' + '","'.join(i.values()) + '"'                                    
            cmd  = 'insert into %s (%s) values (%s)' % (tbl_name,keys,values)
            sql.execute(cmd)
        self._con = con
        self._tbl_name = tbl_name
        self._sql = self._con.cursor()       
        #
    def _calc_fdr_psm(self, dict):
        self._probability_cutoffs = {}
        for k in dict.keys(): 
            sql = self._con.cursor()
            sql2 = self._con.cursor()
            sql.execute('select protein,nrow from %s order by %s desc' % (self._tbl_name,dict[k]))
            t = 0
            f = 0  
            fdr_val = None      
            for row in sql:
                if self._decoy in row[0]: f +=1
                else: t +=1
                fdr_val = float(f) / (float(t) + float(f))
                sql2.execute('update %s set %s=%s where nrow=%s' % (self._tbl_name,k,fdr_val,row[1]))
                               
                
    def _cal_fdr_peptide(self,dict):
        for k in dict.keys(): 
            sql = self._con.cursor()
            sql2 = self._con.cursor()
            sql.execute('select distinct peptide from %s ' % self._tbl_name)
            uniq_peps = [row[0] for row in sql]
            sql.execute('select protein,nrow,peptide from %s order by %s desc' % (self._tbl_name,dict[k]))
            t = 0
            f = 0  
            fdr_val = None      
            for row in sql:
                if row[2] in uniq_peps:
                    uniq_peps.remove(row[2])
                    if self._decoy in row[0]: f +=1
                    else: t +=1
                    fdr_val = float(f) / (float(t) + float(f))
                sql2.execute('update %s set %s=%s where nrow=%s' % (self._tbl_name,k,fdr_val,row[1]))   
            #                                    
    def _run(self,command=None):        
        dict = {'FDR_PPROPHET':'probability_pp','FDR_IPROPHET':'probability_ip'}
        idx = None
        if self._prophet == 'pp': idx = 0
        else: idx =1 
        if self._level == 'psm':
#            key = dict.keys()[idx]
#            dict1 = {key:dict[key]}
            self._calc_fdr_psm(dict)
        else:
#            key = dict.keys()[idx]
#            dict = {key:dict[key]}
            self._cal_fdr_peptide(dict)         
        self._write_tsv(dict.keys()[idx])                     
        print self._get_probability(dict.keys()[idx],dict.values()[idx])
        self._sql.execute('select count(distinct peptide) from %s ' % self._tbl_name)
        self.log.debug('num of uniq peptides [%s]' % self._sql.fetchone()[0])
        self._sql.execute('select count(peptide) from %s ' % self._tbl_name)
        self.log.debug('num of  peptides [%s]' % self._sql.fetchone()[0])
        self._sql.execute('select count(distinct peptide) from %s where %s < %s' % (self._tbl_name,dict.keys()[idx],self._cutoff))
        self.log.debug('num of uniq peptides with cutoff [%s]' % self._sql.fetchone()[0])
        self._sql.execute('select count(peptide) from %s where %s < %s' % (self._tbl_name,dict.keys()[idx],self._cutoff))
        self.log.debug('num of  peptides with cutoff [%s]' % self._sql.fetchone()[0])
        

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
    def _write_tsv(self,col_sort):
        fh = open(self._output_filename, 'w')
        query = 'select * from %s order by %s' % (self._tbl_name, col_sort)
        self.log.debug(query)
        self._sql.execute(query)
        col_name_list = [tuple[0] for tuple in self._sql.description]
        fh.write("\t".join(col_name_list) + "\n")
        for row in self._sql:
            line = '\t'.join([str(i) for i in row])
            fh.write(line + "\n")    
    #   
if '__main__'==__name__:       
    a = Fdr2Probability(use_filesystem=False)
    exit_code = a(sys.argv)
#    print(exit_code)
    sys.exit(exit_code)      