'''
Created on Jan 17, 2011

@author: quandtan
'''

import sys,os
import shutil
from applicake.app import TemplateApplication

class Omssa(TemplateApplication):
    '''
    classdocs
    '''
    def _get_app_inputfilename(self,config):
        src = self._template_filename
        dest = os.path.join(a._wd,'omssa.params')
        shutil.move(src, dest)
        return dest
    
    def _get_command(self,prefix,input_filename):
        search_filename = self._iniFile.read_ini()['SEARCH']
        
        new_mzxml = os.path.join(self._wd,os.path.split(mzxml_filename)[1])
        params = open(input_filename,'r').read()
        self.log.debug('parameter [%s]' % params)
        type = params.split(' ')[0][1:]
        self.log.debug('search file type [%s]' % type)
        basename = os.path.basename(mzxml_filename)
        root= os.path.splitext(basename)[0]        
        self.result_filename  = os.path.join(self._wd,root + "." + type)
        self._iniFile.add_to_ini({'SEARCH':self.result_filename})
        return "ln -s %s %s;%s %s %s" %(mzxml_filename,new_mzxml,prefix,params,new_mzxml)
    
    def _validate_run(self,run_code):               
        return super(Omssa, self)._validate_run(run_code)
        
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
        

