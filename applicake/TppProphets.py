#!/usr/bin/env python
'''
Created on Jan 18, 2011

@author: quandtan
'''

import os,sys,shutil
from applicake.app import Application

class TppProphets(Application):
    '''
    classdocs
    '''
    def _get_app_inputfilename(self,config):
        return None
        
        
    def _get_command(self,prefix,input_filename):
        return prefix    
        
    def _validate_run(self,run_code):  
        return 0            

if "__main__" == __name__:
    # init the application object (__init__)
    a = TppProphets(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)
    
    
# InteractParser -L7 -Etrypsin -C -P # -R lustre   
# PeptideProphetParser DECOY=DECOY_ MINPROB=0 NONPARAM Pd # -R lustre
# RefreshParser # -R lustre
            