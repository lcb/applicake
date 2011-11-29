#!/usr/bin/env python
'''
Created on Nov 29, 2011

@author: quandtan
'''

import os,sys,shutil
from applicake.app import WorkflowApplication
from applicake.utils import XmlValidator

class Dss(WorkflowApplication):

    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        self._code = config['DATASET_CODE']
        self._dataset_dir = config['DATASET_DIR']  
        return "%s %s --out=%s -v -f " % (prefix,self._code,config['DATASET_DIR'])
      
    def _validate_run(self,run_code):     
         
        downloaded_files = open('getdataset.out','r').read()
        filename = downloaded_files.split('\t')[1].split('\n')[0]        
        self._result_filename = filename
        self._iniFile.add_to_ini({'DSSOUTPUT':self._result_filename})
        self.log.debug("add key 'DSSOUTPUT' with value [%s] to ini" % self._result_filename)                       
        # to reset the pointer so that super method works properly
        self.stdout.seek(0)     
        exit_code = super(Dss, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0
      
if "__main__" == __name__:
    # init the application object (__init__)
    a = Dss(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        
