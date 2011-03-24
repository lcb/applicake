'''
Created on Mar 4, 2011
@author: quandtan
'''
#
import sys,os,shutil
from string import Template
from applicake.utils import Utilities
from applicake.app import TemplateApplication
#
class Spectrast(TemplateApplication):
    '''
    classdocs
    '''
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        lib_filename = config['SPECTRASTLIB'] 
        fasta_filename = config['DBASE']             
        self._result_filename  = os.path.join(self._wd,self.name + ".pepXML")
        self._iniFile.add_to_ini({'PEPXML':self._result_filename}) 
        CMD_LINE="${EXEC_PATH} $SEARCH_PARAMS -sL$OUT_DIR_FINAL/spectralibrary.splib -sD$SPECTRAST_DB  -sO$OUT_DIR_RAW $INPUT_PATHS"
        
        
        
        
        ## !!!!CONTINUE HERE
        return '%s %s -sL%s -sD%s -sO' % (prefix,input_filename,lib_filename,fasta_filename ))
    
    
    
    
     
    #       
    def _validate_run(self,run_code):               
        exit_code = super(Spectrast, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0    
    #   
if "__main__" == __name__:
    # init the application object (__init__)
    a = Spectrast(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)