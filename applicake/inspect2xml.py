#!/usr/bin/env python
'''
Created on Feb 1, 2011

@author: quandtan
'''

import os,sys,shutil
from applicake.app import TemplateApplication
from applicake.utils import XmlValidator,Utilities

class Inspect2XML(TemplateApplication):
    '''
    classdocs
    '''
    
    def _get_app_inputfilename(self,config):
        return config['RESULT'] 
    
    def _get_command(self,prefix,input_filename):
        self._result_filename  = os.path.join(self._wd, self.name  + '.pepxml')
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        self.log.debug("add key 'PEPXML' with value [%s] to ini" % self._result_filename)
        # replaces the db and mzxml tags in the original template. the db is not a .trie but a fasta as this is needed by the converter 
        config = self._iniFile.read_ini()
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,output_filename=self._template_filename)
        dir = os.path.split(config['MZXML'])[0]       
        return "%s -i %s -o %s -p %s -m %s -d 1" % (prefix,input_filename,self._result_filename,self._template_filename,dir)     
    
    def _validate_run(self,run_code):                
        exit_code = super(Inspect2XML, self)._validate_run(run_code)
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
    a = Inspect2XML(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)         