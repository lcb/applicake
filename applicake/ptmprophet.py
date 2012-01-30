#!/usr/bin/env python
'''
Created on Jan 26, 2012

@author: quandtan
'''
import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication

class PtmProphet(TemplateApplication):
    '''
    classdocs
    '''
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        pepxml = config['PEPXML']        
        self.log.debug('original pepxml [%s]' % pepxml)        
        params = open(input_filename,'r').read()
        self.log.debug('parameter [%s]' % params)     
        self._result_filename  = os.path.join(self._wd,self.name + ".pep.xml")
        shutil.copy(pepxml,self._result_filename)
        self.log.debug('copied [%s] to [%s] and modify copy' % (pepxml,self._result_filename))
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        self.log.debug('change key [PEPXML] in config to [%s]' % self._result_filename)
        self.log.debug(config)
        return '%s %s %s' % (prefix,params,self._result_filename)        
    
    def _validate_run(self,run_code):               
        exit_code = super(PtmProphet, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0    
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = PtmProphet(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code) 