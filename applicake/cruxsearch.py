#!/usr/bin/env python
'''
Created on Apr 14, 2011

@author: quandtan
'''

import sys,os,shutil
from applicake.crux import Crux

class CruxSearch(Crux):  
    
    def get_crux_command(self):
        # search-for-matches
        return 'search-for-matches'   
    
    def get_pepxml_suffix(self):
        return ".search.target.pep.xml"        
    

if "__main__" == __name__:
    # init the application object (__init__)
    a = CruxSearch(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)