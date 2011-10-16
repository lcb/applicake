#!/usr/bin/env python
'''
Created on Oct 14, 2011

@author: quandtan
'''
import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication
from applicake.utils import Utilities

class Msconvert(TemplateApplication):
    
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        mzxml_filename = self._iniFile.read_ini()['MZXML']        
        return "%s %s -o %s -c %s" %(prefix,mzxml_filename,self._wd,input_filename)
    
    def _run(self,command=None):
        run_code = super(Msconvert, self)._run(command)
        if 0 != run_code:
            return run_code
        ext = None
        stdout = self.stdout.read()
        self.stdout.seek(0)
        for line in stdout.split('\n'):
            if line.startswith('extension'):
                ext = line.split(': ')[1]
        if ext == None:
            self.log.debug('stdout did not contain an extension [%s]' % stdout)        
        self.log.debug('search file extension [%s]' % ext)
        mzxml_filename = self._iniFile.read_ini()['MZXML']
        basename = os.path.basename(mzxml_filename)
        root= os.path.splitext(basename)[0]        
        self._result_filename  = os.path.join(self._wd,root + ext)
        self._iniFile.add_to_ini({'SEARCH':self._result_filename})
        return run_code   
   
    def _validate_run(self,run_code):
        exit_code = super(Msconvert, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0    
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = Msconvert(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)
        