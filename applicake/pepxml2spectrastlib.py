#!/usr/bin/env python
'''
Created on Mar 4, 2011
@author: quandtan
'''
#
import sys,os,shutil
from string import Template
from applicake.app import TemplateApplication
#
class PepXml2SpectrastLib(TemplateApplication):
    '''
    classdocs
    '''
    def _get_command(self,prefix,input_filename):
        rawlib_basename = os.path.join(self._wd,'spectrast_rawlib')
        undecoylib_basename = os.path.join('spectrast_undecoylib')
        uniqlib_basename = os.path.join('spectrast_uniqlib')
        searchlib_basename = os.path.join('spectrast_searchlib')
        lib_ext = '.splib'
        config = self._iniFile.read_ini()
        # in case multiple pepxml files are passed via the key
        pepxml_filename = ' '.join(config['PEPXML'].split(','))      
        probability = config['PROBABILITY'] 
        self.log.debug('split pepxml filename [%s] by [","] and joined by [" "]' % self._pepxml_filename)        
#        content = open(input_filename,'r').read()
#        params = Template(content).safe_substitute(config)
        params = open(input_filename,'r').readlines()
        self.log.debug('parameter [%s]' % params)     
        self._result_filename  = searchlib_basename+lib_ext
        self._iniFile.add_to_ini({'SPECTRASTLIB':self._result_filename}) 
        cmds = []
        cmds.append('%s %s -cP%s -cN%s %s' % (prefix,params[0],probability,rawlib_basename,pepxml_filename))
        cmds.append('%s %s -cN%s' % (prefix,params[1],undecoylib_basename,rawlib_basename+lib_ext))  
        cmds.append('%s %s -cN%s' % (prefix,params[2],uniqlib_basename,undecoylib_basename+lib_ext))  
        cmds.append('%s %s -cN%s' % (prefix,params[3],searchlib_basename,uniqlib_basename+lib_ext))   
        return ';'.join(cmds)   
    #       
    def _validate_run(self,run_code):               
        exit_code = super(PepXml2SpectrastLib, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        return 0    
    #   
if "__main__" == __name__:
    # init the application object (__init__)
    a = PepXml2SpectrastLib(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code) 
        