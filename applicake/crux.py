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
    
    def get_crux_command(self):
        # search-for-matches
        raise NotImplementedError("Called 'get_crux_command' method on abstact class")     
    
    def get_pepxml_suffix(self):
        # ".search.target.pep.xml"
        raise NotImplementedError("Called 'get_pepxml_suffix' method on abstact class")         
    
    def _get_app_inputfilename(self,config):
        dest = os.path.join(self._wd,self.name + self._params_ext)
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
        db_filename = db_filename + '.idx'   
        self._result_filename  = os.path.join(self._wd,self.name + self.get_pepxml_suffix())
        self._iniFile.add_to_ini({'PEPXML':self._result_filename})
        # crux search-for-matches --parameter-file my.params --fileroot B08-02057 B08-02057.mzXML --output-dir . /cluster/scratch/malars/databases/AE004092_sp_9606.idx
        return "%s %s --parameter-file %s --fileroot %s %s --output-dir %s %s" %(prefix,self.get_crux_command(),input_filename,self.name,search_filename,self._wd,db_filename)
    
#    def _validate_run(self,run_code):                       
#        raise NotImplementedError("Called '_validate' method on abstact class") 
#    
    def _validate_run(self,run_code):               
        exit_code = super(Crux, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0
#        stderr = self.stderr.read()
#        if 'INFO: Return Code:0' in stderr:
#            self.log.debug('crux finished %s' % self.get_crux_command())
#            return 0
#        else:         
##        for line in self.stderr.read():
##            if line.startswith('INFO: Return Code:0'):
##                self.log.debug('crux finished %s' % self.get_crux_command())
##                return 0                
#            self.log.error("crux did not finish %s properly" % self.get_crux_command())
#            self.log.debug(stderr)
#            self.log.debug(self.stderr.read())
#            return 1       