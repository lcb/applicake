#!/usr/bin/env python
'''
Created on Jan 25, 2011

@author: quandtan
'''

import sys,os,shutil
from string import Template
from applicake.app import SequenceTemplateApplication

class ProteinProphet(SequenceTemplateApplication):
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
        protxml_filename  = os.path.join(self._wd,self.name + ".protxml")
        protxml_sc_filename  = os.path.join(self._wd,self.name + "_spectralcount.protxml")
        self._result_filename  = os.path.join(self._wd,self.name + "_openbis.protxml")
        self._iniFile.add_to_ini({'PROTXML':self._result_filename})
        
         # prefix is for this class a [] instead of a string
        prefixes = prefix
        self.log.debug('prefixes [%s]' %prefixes)
        if len(prefixes) != 3:
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
            # ProteinProphet <interact_pepxml_file1> [<interact_pepxml_file2>[....]] <output_protxml_file> (ICAT) (GLYC) (XPRESS) (ASAP_PROPHET) (ACCURACY) (ASAP) (PROTLEN) (NOPROTLEN) (NORMPROTLEN) (GROUPWTS) (INSTANCES) (REFRESH) (DELUDE) (NOOCCAM) (NOPLOT) (PROTMW)
            cmds.append('%s %s %s %s' % (prefixes[0],pepxml_filename,protxml_filename,params[0]))
            # protxml2spectralcount [Options] <protXML>
            cmds.append('%s -CSV=%s -OUT=%s %s %s' % (prefixes[1],csv_filename,protxml_sc_filename,params[1],protxml_filename))
            # protxml2openbis [Options] <protXML>
            cmds.append('%s -DB=%s -OUT=%s %s %s' % (prefixes[2],db,self._result_filename,params[2],protxml_sc_filename))                
        return ';'.join(cmds)       
    
    
    def _validate_run(self,run_code):               
        
        if 0 != run_code:
            # return exit_code    
            self.log.warning('ignore run_code [%s]' % exit_code)
        exit_code = super(ProteinProphet, self)._validate_run(0)
        if exit_code != 0:
            return     
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