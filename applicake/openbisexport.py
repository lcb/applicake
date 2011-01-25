#!/usr/bin/env python
'''
Created on Jan 25, 2011

@author: quandtan
'''
import sys,os,shutil
from string import Template
from applicake.app import SequenceTemplateApplication

class OpenbisExport(SequenceTemplateApplication):
    '''
    classdocs
    '''
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        protxml_filename = config['PROTXML']        
        self.log.debug('PROTXML [%s]' % protxml_filename)
        csv_filename = config['CSV']        
        self.log.debug('CSV [%s]' % csv_filename)
        db = config['DBASE']
        self.log.debug('DBASE [%s]' % db)        
        content = open(input_filename,'r').read()        
        params = Template(content).safe_substitute(config)
        self.log.debug('parameter [%s]' % params)   
        protxml_sc_filename  = os.path.join(self._wd,self.name + "_spectralcount.protxml")
        self._result_filename  = os.path.join(self._wd,self.name + ".protxml")
        self._iniFile.update_ini({'PROTXML':self._result_filename})        
         # prefix is for this class a [] instead of a string
        prefixes = prefix
        self.log.debug('prefixes [%s]' %prefixes)
        if len(prefixes) != 2:
            self.log.fatal('number of prefixes is not correct [%s]' % len(prefixes))
            sys.exit(1)        
        params = open(input_filename,'r').readlines()
        self.log.debug('splitted params [%s]' %params)
        cmds = None
        if not len(prefixes)==len(params):
            self.log.fatal('number of prefixes [%s] does not match number of params [%s]' % (len(prefixes),len(params)))
            sys.exit(1)
        else:
            cmds = []
            # protxml2spectralcount [Options] <protXML>
            cmds.append('%s -CSV=%s -OUT=%s %s %s' % (prefixes[0],csv_filename,protxml_sc_filename,params[0],protxml_filename))
            # protxml2openbis [Options] <protXML>
            cmds.append('%s -DB=%s -OUT=%s %s %s' % (prefixes[1],db,self._result_filename,params[1],protxml_sc_filename))                
        return ';'.join(cmds)       
    
    
    def _validate_run(self,run_code):               
        exit_code = super(OpenbisExport, self)._validate_run(0)
        if exit_code != 0:
            return  exit_code
        return 0   
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = OpenbisExport(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)   
        