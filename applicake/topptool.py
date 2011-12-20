'''
Created on Nov 30, 2011

@author: quandtan
'''

import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication
from applicake.utils import Utilities

class Topptool(TemplateApplication):      
    '''
    description
    '''      
    
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()        
        mzxml_filename = config['SEARCH']
        db_filename = config['DBASE']
        basename = os.path.splitext(os.path.split(mzxml_filename)[1])[0]    
        self._result_filename  = os.path.join(self._wd,basename + ".pepXML")
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        # myrimatch -ProteinDatabase AE004092_sp_9606.fasta B08-02057_p.mzXML 
        return "%s -cpu 8 -cfg %s -workdir %s -ProteinDatabase %s %s" %(prefix,input_filename,self._wd,db_filename,mzxml_filename)
   
    def _validate_run(self,run_code):               
        exit_code = super(Topptool, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0    
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = Topptool(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)