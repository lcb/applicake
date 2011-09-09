'''
Created on Sep 9, 2011

@author: quandtan
'''
import os,sys,shutil,logging
from applicake.app import TemplateApplication


class ProtXml2SpectralCount(TemplateApplication):
    '''
    classdocs
    '''
    #


#import csv
#import cStringIO
#from collections import Counter
#data = open("0-pepxml2csv.csv").read()
#reader = csv.DictReader(cStringIO.StringIO(data),delimiter='\t')
#peptides = [row['peptide'] for row in reader]
#cnt = Counter(peptides)
#cnt.items()
#
#t = ['LNAEYGNVGNNEETLDDH','LQELFTPK','ALPPHVDMFYTGRIYQSAFGGFHVEDFVVSDPWALGHLR','KSAELSTELSTEPPSSSSEDDK']
#sum(cnt[e] for e in t)      
                          

if "__main__" == __name__:
    # init the application object (__init__)
    a = ProtXml2SpectralCount(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code) 