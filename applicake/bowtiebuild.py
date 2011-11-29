#!/usr/bin/env python
'''
Created on Nov 29, 2011

@author: quandtan
'''

import os, sys, shutil, glob
from applicake.app import WorkflowApplication

class BowtieBuild(WorkflowApplication):

    def _get_command(self, prefix, input_filename):
        config = self._iniFile.read_ini()
        ref = config['REFERENCE_GENOME']
        out_fname =  '%s%s' % (self.name,self._result_ext)  
        self._result_filename  = os.path.join(self._wd, out_fname)
        self._iniFile.add_to_ini({'BOWTIEBUILD': self._result_filename})
        return "%s -f %s %s" % (prefix, ref, self._result_filename)
        
  
    
    def _validate_run(self, run_code):
        # does any output exist?
        if glob.glob(self._result_filename + "*.ebwt"): 
            return 0
        return 1              

      
if "__main__" == __name__:
    # init the application object (__init__)
    a = BowtieBuild(use_filesystem=True, name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename, a._stderr_filename, a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        