#!/usr/bin/env python
'''
Created on Jun 22, 2011

@author: quandtan
'''
#!/usr/bin/env python
'''
Created on Jan 10, 2011

@author: quandtan
'''
#
import os,sys,shutil
from applicake.app import WorkflowApplication
from applicake.utils import XmlValidator



#[schmide@brutus3 jython-api]$ ./jythonapi 20100917190027979-54174
#*sys-package-mgr*: can't create package cache dir, '/cluster/apps/jython/2.5.2/cachedir/packages'
#20100917190027979-54174 20100917190027979-54174 ./O08-10096_c.mzXML

class Dss(WorkflowApplication):

    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        self._code = config['DATASET_CODE']
        self._dataset_dir = config['DATASET_DIR']
#        return "%s --out=%s -v %s" % (prefix,self._wd,self._code) # where putting in the work directory  
        return "%s --out=%s -v %s" % (prefix,config['DATASET_DIR'],self._code)
  
    
    def _validate_run(self,run_code):     
         
        for line in self.stdout.readlines():  
            line  = line          
            if line.startswith(self._code):
                found = 1
                arr = line.split('\t')                                 
                mzxml_filename = arr[2].rstrip('\n')                
                if not mzxml_filename.lower().endswith('mzxml'):
                    self.log.error('mzxml file [%s] did not end with "mzxml" (case insensitive)'% mzxml_filename)
                    stderr = self.stderr.read()
                    self.stderr.seek(0)    
                    if "already exists" in stderr:
                        self.log.debug('mzxml file already exists')
                        for e in stderr.split(' '):
                            if e.lower().endswith('mzxml'):
                                mzxml_filename = e
                    else:
                        self.log.fatal('mzxml file did not exist previously.')
                        return 1                                
                self._result_filename = os.path.join(self._dataset_dir,mzxml_filename)
                self._iniFile.add_to_ini({
                                          'MZXML':self._result_filename,
                                          'SEARCH':self._result_filename})
                self.log.debug("add key 'MZXML' with value [%s] to ini" % self._result_filename)                       
        # to reset the pointer so that super method works properly
        self.stdout.seek(0)     
        exit_code = super(Dss, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0
      
if "__main__" == __name__:
    # init the application object (__init__)
    a = Dss(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        