#!/usr/bin/env python
'''
Created on Jan 14, 2011

@author: quandtan
'''

import sys,os
import shutil
from applicake.app import TemplateApplication

class MzXML2Search(TemplateApplication):
    '''
    classdocs
    '''

    def _get_app_inputfilename(self,config):
        src = self._template_filename
        dest = os.path.join(a._wd,'mzxml2search.params')
        shutil.move(src, dest)
        return dest
    
    def _get_command(self,prefix,input_filename):
        mzxml_filename = self._iniFile.read_ini()['MZXML']
        params = open(input_filename,'r').read()
        self.log.debug('parameter [%s]' % params)
        type = params.split(' ')[0][1:]
        self.log.debug('search file type [%s]' % type)
        self.search_filename  = os.path.join(self._wd,'search.' + type)
        self._iniFile.add_to_ini({'SEARCH':self.search_filename})
        return "%s %s" %(prefix,params,mzxml_filename,self.search_filename)
    
    def _validate_run(self,run_code):       
        result = self.search_filename
        output = os.path.abspath(self._output_filename)
        if 0 < run_code:
            return run_code 
        if not os.path.exists(result):
            self.log.error('File [%s] does not exist' % result)
            return 1
        else:
            self.log.debug('File [%s] does exist' % result)
        if not os.path.exists(output):
            self.log.error("File [%s] does not exist" % output)
            return 1
        else:
            self.log.debug("File [%s] does exist" % output)
            self.log.debug("content:%s" % self._iniFile.read_ini())               
        return 0  
        
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
        