#!/usr/bin/env python
'''
Created on Jan 25, 2011

@author: quandtan
'''
import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication

class InterProphet(TemplateApplication):
    '''
    classdocs
    '''

    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        # in case multiple pepxml files are passed via the key
        self._pepxml_filename = ' '.join(config['PEPXML'].split(','))        
        self.log.debug('split pepxml filename [%s] by [","] and joined by [" "]' % self._pepxml_filename)        
        content = open(input_filename,'r').read()
        params = Template(content).safe_substitute(config)
        self.log.debug('parameter [%s]' % params)     
        self._result_filename  = os.path.join(self._wd,self.name + ".pep.xml")
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        return '%s %s %s %s' % (prefix,params,self._pepxml_filename,self._result_filename)        
    
    def _validate_run(self,run_code):               
        exit_code = super(InterProphet, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        for line in self.stderr.readlines():
            if 'fin: error opening' in line:
                self.log.error("could not read the input file [%s]" % self._pepxml_filename)
                return 1
        return 0    
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = InterProphet(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        