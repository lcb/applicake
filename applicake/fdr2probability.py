'''
Created on Feb 21, 2011

@author: quandtan
'''
#
import argparse,os,sys,tablib,fileinput,logging,glob
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
    def _preprocessing(self):
        self.log.debug('generate data obj from input file')
        self._data = tablib.Dataset()
        header=True
        for line in fileinput.input(self._input_filename):
            arr = line.replace('\n','').split(self.sep)
            if header: 
                self._data.headers = arr
                header = False 
            else: 
                self._data.append(arr)       
        #

    def _calc_fdr_psm(self, dict):
        for k in dict.keys(): 
            #            self._data.headers.append(k)
            self._data = self._data.sort(dict[k], reverse=True) 
            #            T=[]
            t = 0 
            #            F=[]
            f = 0
            fdr = []
            for e in self._data['protein']:
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
            #            self._data.headers.append(k)
#            self._data = self._data.sort(dict[k], reverse=True)
            uniq_peps = list(set(self._data['peptide']))  
            l = len(uniq_peps)
            T=[]
            t = 0 
            F=[]
            f = 0
            fdr = []       
            for i,e in enumerate(self._data['peptide']):
                if e in uniq_peps:
                    uniq_peps.remove(e)
                    if self._decoy in self._data['protein'][i]:
                        f += 1
                    else:
                        t += 1   
                T.append(t)
                F.append(f)                        
                fdr.append(float(f) / (float(t) + float(f))) 
            
            assert l == (T[-1]+F[-1]) 
            self._data.append(col=T, header='T')            
            self._data.append(col=F, header='F')
            self._data.append(col=fdr, header=k)                                        
            
            
            

    def _run(self,command=None):        
        dict = {'FDR_PPROPHET':'probability_pp','FDR_IPROPHET':'probability_ip'}
        if self._level is 'psm':
            self._calc_fdr_psm(dict)
        else:
            self._cal_fdr_peptide(dict)
        print self._data.headers
        print self._data.tsv
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
    print(exit_code)
    sys.exit(exit_code)      

    