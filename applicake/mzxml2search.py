#!/usr/bin/env python
'''
Created on Jan 14, 2011

@author: quandtan
'''

import sys,os
import shutil
from applicake.app import TemplateApplication

class MzXML2Search(TemplateApplication):
    
    def _get_command(self,prefix,input_filename):
        mzxml_filename = self._iniFile.read_ini()['MZXML']
        new_mzxml = os.path.join(self._wd,os.path.split(mzxml_filename)[1])
        params = open(input_filename,'r').read()
        self.log.debug('parameter [%s]' % params)
        type = params.split(' ')[0][1:]
        self.log.debug('search file type [%s]' % type)
        basename = os.path.basename(mzxml_filename)
        root= os.path.splitext(basename)[0]        
        self._result_filename  = os.path.join(self._wd,root + "." + type)
        self._iniFile.add_to_ini({'SEARCH':self._result_filename})
        return "ln -s %s %s;%s %s %s" %(mzxml_filename,new_mzxml,prefix,params,new_mzxml)
    
    def _validate_run(self,run_code):               
        return super(MzXML2Search, self)._validate_run(run_code)
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = MzXML2Search(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)
        