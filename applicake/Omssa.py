#!/usr/bin/env python
'''
Created on Jan 17, 2011

@author: quandtan
'''

import sys,os
import shutil
from string import Template
from applicake.app import TemplateApplication
from applicake.utils import Utilities

class Omssa(TemplateApplication):
    '''
    classdocs
    '''
    def _get_app_inputfilename(self,config):
        dest = os.path.join(self._wd,'omssa' + self._params_ext)
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,output_filename=dest)
        return dest        
    
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        search_filename = config['SEARCH']
        content = open(input_filename,'r').read()
        params = Template(content).safe_substitute(config)
        self.log.debug('parameter [%s]' % params)
        if config['PRECMASSUNIT'].lower() is "ppm":
            params = params + ' -teppm'
            self.log.debug('added [ -teppm] to parameters')       
        self._result_filename  = os.path.join(self._wd,self.name + ".pepxml")
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
#        ' -fm '+input_path+' -op '+ output_path+
        return "%s %s -fm %s -op %s" %(prefix,params,search_filename,self._result_filename)
    
    def _validate_run(self,run_code):               
        exit_code = super(Omssa, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        for line in self.stderr.readlines():
            if not line.startswith('Info:'):
                self.log.error("stderr contains following line [%s]" % line)
                return 1
        return 0    
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = Omssa(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)
        
