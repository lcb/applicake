#!/usr/bin/env python
'''
Created on Jan 27, 2011

@author: quandtan
'''
import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication
from applicake.utils import Utilities

class Myrimatch(TemplateApplication):      
    '''
    description
    '''
    def _get_app_inputfilename(self,config):
        dest = os.path.join(self._wd,self.name + self._params_ext)
        if config['FRAGMASSUNIT'] == 'Da':
            self.log.debug("replace 'FRAGMASSUNIT' with value [Da] to [daltons]")
            config['FRAGMASSUNIT'] ='daltons'
        self.log.debug(config)   
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,output_filename=dest)
        return dest      
    
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()        
        mzxml_filename = config['SEARCH']
        db_filename = config['DBASE']
        basename = os.path.splitext(os.path.split(mzxml_filename)[1])[0]    
        self._result_filename  = os.path.join(self._wd,basename + ".pepXML")
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        # myrimatch -ProteinDatabase AE004092_sp_9606.fasta B08-02057_p.mzXML 
        return "%s -cpus 8 -cfg %s -workdir %s -ProteinDatabase %s %s" %(prefix,input_filename,self._wd,db_filename,mzxml_filename)
   
    def _validate_run(self,run_code):               
        exit_code = super(Myrimatch, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0    
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = Myrimatch(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)
        