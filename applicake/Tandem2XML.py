#!/usr/bin/env python
'''
Created on Jan 10, 2011

@author: quandtan
'''

import os,sys,shutil,argparse,string
from applicake.app import WorkflowApplication
from applicake.utils import XmlValidator

class Tandem2XML(WorkflowApplication):
    
    def _get_app_inputfilename(self,config):
        return config['RESULT'] 
    
    def _get_command(self,prefix,input_filename):
        self._result_filename  = os.path.join(self._wd, self.name  + '.pepxml')
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        self.log.debug("add key 'PEPXML' with value [%s] to ini" % self._result_filename)
        return "%s %s %s" % (prefix,input_filename,self._result_filename)     
    
    def _validate_run(self,run_code):                
        exit_code = super(Tandem2XML, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        if not XmlValidator(self._result_filename).is_wellformatted():
            self.log.error('File [%s] is not well-formed' % self._result_filename)
            return 1
        else:
            self.log.debug('File [%s] is well-formed'% self._result_filename )
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