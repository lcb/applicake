#!/usr/bin/env python
'''
Created on Jan 18, 2011

@author: quandtan
'''

import os,sys,shutil,argparse,glob
from applicake.app import WorkflowApplication
from applicake.omssa import Omssa 
from applicake.app import ExternalApplication
from applicake.utils import IniFile

class TppProphets(WorkflowApplication):
    '''
    classdocs
    '''
    def _get_parsed_args(self):
        parser = argparse.ArgumentParser(description='Wrapper around a spectra identification application')
        parser.add_argument('-t','--tandem',nargs=1,action="store", dest="tandem",type=str,help="xtandem ini file pattern")
        parser.add_argument('-o','--omssa',nargs=1,action="store", dest="omssa",type=str,help="omssa ini file pattern")
        a = parser.parse_args()
        return {'tandem':a.tandem,'omssa':a.omssa}         

    
    def _preprocessing(self):
        self._iniFile = IniFile(input_filename=self._config_filename,lock=False) 
        self.log.debug('Start [%s]' % self._iniFile.read_ini.__name__)
        config = self._iniFile.read_ini()
        self.log.debug('Finished [%s]' % self._iniFile.read_ini.__name__)
        self.log.info('Start %s' % self.create_workdir.__name__)
        self._wd = self.create_workdir(config)
        self.log.info('Finished %s' % self.create_workdir.__name__)   
        self._iniFile.add_to_ini({'DIR':self._wd})
        self.log.debug("add key 'DIR' with value [%s] to ini" % self._wd)      
    
    def _run(self,command=None):    
        try:            
            a = ExternalApplication(use_filesystem=True,name=None)
            a(['ls -lah'])
            return 0
        except Exception,e:
            self.log.exception(e)
            return 1           

    def _validate_parsed_args(self,dict):
        if dict['tandem'] is not None:
            for filename in glob.glob("%s*" % dict['tandem']):
                print filename
        if dict['omssa'] is not None:
            for filename in glob.glob("%s*" % dict['omssa']):
                print filename            

    def _validate_run(self,run_code=None):
        self.log.debug('not implemented')       

if "__main__" == __name__:
    # init the application object (__init__)
    a = TppProphets(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)
    
    
# InteractParser -L7 -Etrypsin -C -P # -R lustre   
# PeptideProphetParser DECOY=DECOY_ MINPROB=0 NONPARAM Pd # -R lustre
# RefreshParser # -R lustre
            