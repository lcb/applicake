#!/usr/bin/env python
'''
Created on Mar 30, 2011

@author: quandtan
'''

import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication
from applicake.utils import Utilities

class Crux(TemplateApplication):      
    
    def _get_app_inputfilename(self,config):
        dest = os.path.join(self._wd,self.name + self._params_ext)
        db = config['DBASE']
        config['DBASE'] = db.replace('.fasta','.idx')
        if(config['PRECMASSUNIT'] == 'Da'):
            config['PRECMASSUNIT'] = 'mz'
        self._iniFile.write_ini(config) 
        self.log.debug(config)   
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,output_filename=dest)
        return dest               
    
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        search_filename = config['MZXML']
        db_filename = config['DBASE']    
        self._result_filename  = os.path.join(self._wd,self.name + ".search.target.pep.xml")
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        # crux search-for-matches --parameter-file my.params --fileroot B08-02057 B08-02057.mzXML --output-dir . /cluster/scratch/malars/databases/AE004092_sp_9606.idx
        return "%s search-for-matches --parameter-file %s --fileroot %s %s --output-dir %s %s" %(prefix,input_filename,self.name,search_filename,self._wd,db_filename)
    
    def _validate_run(self,run_code):               
        exit_code = super(Crux, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        for line in self.stderr.readlines():
            if line.startswith('INFO: Finished crux-search-for-matches'):
                self.log.debug('crux finished search-for-matches')
                return 0                
        self.log.error("crux did not finish search-for-matches properly")
        return 1
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = Crux(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)