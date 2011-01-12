#!/usr/bin/env python
'''
Created on Jan 10, 2011

@author: quandtan
'''

import os,sys,shutil,argparse,string
from applicake.app import WorkflowApplication

class Tandem2XML(WorkflowApplication):
    
    def _get_app_inputfilename(self,config):
        return config['RESULT'] 
    
    def _get_command(self,prefix,input_filename):
        self.pepxml_filename  = os.path.join(self._wd,'tandem.pepxml')
        self._iniFile.add_to_ini({'PEPXML':self.pepxml_filename})
        return "%s %s %s" % (prefix,input_filename,self.pepxml_filename)     
    
    
    def _validate_run(self,run_code):        
        if 0 < run_code:
            return run_code 
        if not os.path.exists(self.pepxml_filename):
            self.log.error('File [%s] does not exist' % os.path.abspath(self.pepxml_filename))
            return 1
        else:
            self.log.debug('File [%s] does exist' % os.path.abspath(self.pepxml_filename))
        if not os.path.exists(self._output_filename):
            self.log.fatal("File [%s] does not exist" % os.path.abspath(self._output_filename))
            return 1
        else:
            self.log.debug("File [%s] does exist" % os.path.abspath(self._output_filename))               
        return 0       

if "__main__" == __name__:
    # init the application object (__init__)
    a = Tandem2XML(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        