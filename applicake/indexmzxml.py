#!/usr/bin/env python
'''
Created on Jan 26, 2012

@author: quandtan
'''
import os,sys,shutil
from applicake.app import WorkflowApplication
from applicake.utils import XmlValidator

class IndexMzxml(WorkflowApplication):
    
    def _get_app_inputfilename(self,config):
        return config['MZXML'] 
    
    def _get_command(self,prefix,input_filename):
        dir = os.path.dirname(input_filename)               
        self._result_filename  = input_filename.replace(dir,self._wd)
        config = self._iniFile.read_ini() 
        config['MZXML'] = self._result_filename
        config['SEARCH'] = self._result_filename
        self._iniFile.write_ini(config)
        self.log.debug(" modified key 'SEARCH' to value [%s] and wrote ini" % self._result_filename)
        self.log.debug('will symlink [%s] to [%s]' % (input_filename, self._result_filename))
        return "ln -s %s %s;%s %s" % (input_filename, self._result_filename, prefix,self._result_filename)  
       
    
    def _validate_run(self,run_code):                
        exit_code = super(IndexMzxml, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        stdout = self.stdout.read()
        if 'The index is corrupted' in stdout:
            output_file = ''.join([self._result_filename,'.new'])
            self.log.debug('index of [%s] was corrupt and [%s] was created' %(self._result_filename,output_file))            
            shutil.move(output_file,self._result_filename)
            self.log.debug('moved [%s] to [%s]' % (output_file, self._result_filename))   
        else:
            self.log.debug('index of [%s] was correct' % self._input_filename)         
        return 0       

if "__main__" == __name__:
    # init the application object (__init__)
    a = IndexMzxml(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        