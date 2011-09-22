#!/usr/bin/env python
'''
Created on Jan 31, 2011

@author: quandtan
'''

import sys,os
import shutil
from applicake.app import TemplateApplication
from applicake.utils import Utilities

class Inspect(TemplateApplication):
    
    def _get_app_inputfilename(self,config):
        db = config['DBASE']
        ext = db.split('.')[-1]
        config['DBASE'] = db.replace('.%s'%ext,'.trie')
        input_filename = os.path.join(self._wd, self.name + self._params_ext )  
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,output_filename=input_filename)
        fh = open(input_filename, "a")   
        fh.write('\n')  
        if(config['PRECMASSUNIT'] == 'Da'):
            fh.write('PMTolerance,%s\n' % config['PRECMASSERR'])
        else:
            fh.write('ParentPPM,%s\n' % config['PRECMASSERR'])
        if(config['FRAGMASSUNIT'] == 'Da'):
            fh.write('IonTolerance,%s\n' % config['FRAGMASSERR'])
        else:
            fh.write('PeakPPM,%s\n' % config['FRAGMASSERR'])                
        return input_filename    
        
        
    def _get_command(self,prefix,input_filename):
        self._result_filename = os.path.join(self._wd,self.name + self._result_ext)
        self._iniFile.add_to_ini({'RESULT':self._result_filename})
        self.log.debug("add key 'RESULT' with value [%s] to ini" % self._result_filename)
        return "%s -i %s -o %s" % (prefix,input_filename,self._result_filename)    
          
    def _validate_run(self,run_code):  
        exit_code = super(Inspect, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
#        stdout = self.stdout.read()            
        stderr = self.stderr.read()
        if "Unable to open requested file " in stderr:
            self.log.error('could not open requested file. Most likely Resource dir has to be set correctly')
            return 1
        file_size =  os.path.getsize(self._result_filename) 
        if file_size <1:
            self.log.error('result file is too small [%s] kb' % str(file_size))
        return 0            

if "__main__" == __name__:
    # init the application object (__init__)
    a = Inspect(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)