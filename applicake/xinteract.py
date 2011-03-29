#!/usr/bin/env python
'''
Created on Jan 19, 2011

@author: quandtan
'''
import os,sys,shutil
from applicake.app import TemplateApplication

class Xinteract(TemplateApplication):
    
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        pepxml_filename = config['PEPXML']        
        db_filename = config['DBASE']
        self._result_filename  = os.path.join(self._wd, self.name  + '.pep.xml')
        self._iniFile.update_ini({'PEPXML':self._result_filename})
        self.log.debug("updated key 'PEPXML' with value [%s] in ini" % self._result_filename)      
        params = open(input_filename,'r').read()
        self.log.debug('parameter [%s]' % params)
        # xinteract -Ndata.pep.xml -X -Op
        return '%s -N%s %s %s' % (prefix,self._result_filename,params,pepxml_filename)
    
    def _validate_run(self,run_code):                
        exit_code = super(Xinteract, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        stdout = self.stdout.read()
        stderr = self.stderr.read()
        if 'No decoys with label' in stderr:
            self.log.error('found no decoy hits')
            return 1             
        else:
            self.log.debug('did find decoy hits')        
        if 'exited with non-zero exit code' in stdout:
            self.log.error('xinteract did not complete with exit code !=0')
            return 1
        else:
            self.log.debug('xinteract finished with normal exit code')
        if 'QUIT - the job is incomplete' in stdout:
            self.log.error('xinteract: job is incomplete')
            return 1
        else:
            self.log.debug('job is completed')
        return 0       

if "__main__" == __name__:
    # init the application object (__init__)
    a = Xinteract(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)    
        