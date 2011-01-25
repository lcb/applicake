#!/usr/bin/env python
'''
Created on Jan 25, 2011

@author: quandtan
'''

import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication

class ProteinProphet(TemplateApplication):
    '''
    classdocs
    '''
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        pepxml_filename = config['PEPXML']
        self.log.debug('PEPXML [%s]' % pepxml_filename)
        csv_filename = config['CSV']        
        self.log.debug('CSV [%s]' % csv_filename)
        db = config['DBASE']
        self.log.debug('DBASE [%s]' % db)        
        content = open(input_filename,'r').read()        
        params = Template(content).safe_substitute(config)
        self.log.debug('parameter [%s]' % params)   
        self._result_filename  = os.path.join(self._wd,self.name + ".protxml")
        self._iniFile.add_to_ini({'PROTXML':self._result_filename})        
        return '%s %s %s %s' % (prefix,pepxml_filename,self._result_filename,params)      
    
    def _validate_run(self,run_code):                       
        if 0 != run_code:
            # return exit_code    
            self.log.warning('ignore run_code [%s]' % run_code)
        exit_code = super(ProteinProphet, self)._validate_run(0)
        if exit_code != 0:
            return exit_code    
        stdout = self.stdout.read()
        msg = 'No xml file specified; please use the -file option'
        if msg in stdout:
                self.log.debug('ProteinProphet ignore [%s] of protxml2html' % msg)               
        for msg in ['did not find any InterProphet results in input data!',
                    'no data - quitting',
                    'WARNING: No database referenced']:
            if msg in stdout:
                self.log.error('ProteinProphet error [%s]' % msg)
                return 1
            else:
                self.log.debug('ProteinProphet: passed check [%s]' % msg)
        return 0 
 
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = ProteinProphet(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        