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
    Usage:
  FDR2Probability  [Options] <CSVfile>

This program adds protein information from the CSV file to the prot.xml file (parameter tags) 
  Options: 
                    [-?]                 - Show usage and exit 
                    [-V]                 - Verbose Mode 
                    [-IPROPHET]          - Use also iProphet probability (default only pepProphet)
                    [-DECOY=<decoy_tag>]         - Decoy tag in protein name (default: "DECOY_") 
                    [-FDR=<cutoff>]      - FDR cut-off (default: 0.01) 
                    [-OUT=<newCSV>]      - New CSV file with added FDR column(s)
                    CSVfile              - CSV file from iproph.pepXML
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
    def _get_probability(self,fdr_col,prob_col,cutoff):
        q1 = None
        for i,e in enumerate(self._data.sort(fdr_col)[fdr_col]):
            if(cutoff <= e): 
                q1 = float(self._data[prob_col][i])
                break
        return q1               
        #
    def _preprocessing(self):
        self.log.debug('read [%s]' % self._input_filename)
        reader = csv.DictReader(open(self._input_filename), delimiter='\t')
        header = reader.fieldnames
        new_col_names = ['FDR_PPROPHET','FDR_IPROPHET']      
        self.log.debug('init in-memory db')
        tbl_name = 'pepcsv'
        con = sqlite3.connect(':memory:')        
        # If you want autocommit mode, then set isolation_level to None
        con.isolation_level = None
        sql = con.cursor()
#        cols = ["id INT PRIMARY KEY"]
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
        self._sql = sql
        self._tbl_name = tbl_name
#        self._c.executemany("insert into t (col1, col2) values (?, ?);", to_db)       
        #
    def _calc_fdr_psm(self, dict):
        self._probability_cutoffs = {}
        for k in dict.keys(): 
            #            self._data.headers.append(k)
            self._data = self._data.sort(dict[k], reverse=True) 
            #            T=[]
            t = 0 
            #            F=[]
            f = 0
            fdr = []
            for i,e in enumerate(self._data['protein']):
                if self._decoy in e:
                    f += 1
                else:
                    t += 1
    #                T.append(t)
    #                F.append(f)
                fdr.append(float(f) / (float(t) + float(f))) 
    #            self._data.append(col=T, header='T')            
    #            self._data.append(col=F, header='F')
            self._data.append(col=fdr, header=k)
            #
    def _cal_fdr_peptide(self,dict):
        for k in dict.keys(): 
            self._data = self._data.sort(dict[k], reverse=True)
            uniq_peps = list(set(self._data['peptide']))  
            l = len(uniq_peps)
            t = 0 
            f = 0
            fdr = []       
            for i,e in enumerate(self._data['peptide']):
                if e in uniq_peps:
                    uniq_peps.remove(e)
                    if self._decoy in self._data['protein'][i]:
                        f += 1
                    else:
                        t += 1                          
                fdr.append(float(f) / (float(t) + float(f))) 
            assert l == t+f
            self._data.append(col=fdr, header=k)    
            #                                    
    def _run(self,command=None):        
        dict = {'FDR_PPROPHET':'probability_pp','FDR_IPROPHET':'probability_ip'}
        self._sql.execute('select spectrum from %s order by probability_pp limit 5' % tbl_name)
        for row in self._sql:
            print row[0]
        sys.exit(1)
        #
        #
        #
        if self._level is 'psm':
            self._calc_fdr_psm(dict)
        else:
            self._cal_fdr_peptide(dict)
        idx = None
        if self._prophet == 'ip': idx = 0
        else: idx =1 
        with open(self._output_filename, 'w') as f: 
            f.write(self._data.tsv)          
        prob = self._get_probability(dict.keys()[idx],dict.values()[idx],self._cutoff)
        cutoff_limit = 0.001
        if prob < cutoff_limit: 
            prob = cutoff_limit
        print prob         
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
    #   
if '__main__'==__name__:       
    a = Fdr2Probability(use_filesystem=False)
    exit_code = a(sys.argv)
#    print(exit_code)
    sys.exit(exit_code)      

    