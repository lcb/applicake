#!/usr/bin/env python
'''
Created on Nov 17, 2010

@author: quandtan
'''
import sys,os
import shutil
from applicake.app import TemplateApplication
from applicake.utils import Utilities

class Tandem(TemplateApplication):
    
    def _get_app_inputfilename(self,config):
        default_filename = os.path.join(self._wd,'default' + self._params_ext )            
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,output_filename=default_filename)
        self.log.debug('Created [%s]' % default_filename)
        taxonomy_filename = os.path.join(self._wd,'taxonomy' + self._params_ext)
        db_filename = None
        spectra_filename = None
        self._result_filename = None        
        try:
            db_filename = config['DBASE']
            spectra_filename = config['SEARCH']
            self._result_filename = os.path.join(self._wd,self.name + self._result_ext)
        except Exception,e:
            self.log.exception(e)
            sys.exit(1)           
        with open(taxonomy_filename, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write('<bioml>\n<taxon label="database">')
            sink.write('<file format="peptide" URL="%s"/>' % db_filename)
            sink.write("</taxon>\n</bioml>")
        self.log.debug('Created [%s]' % taxonomy_filename)
        input_filename = os.path.join(self._wd, self.name + self._params_ext )    
        with open(input_filename, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write("<bioml>\n<note type='input' label='list path, default parameters'>"+default_filename+"</note>\n")
            sink.write("<note type='input' label='output, xsl path' />\n<note type='input' label='output, path'>"+self._result_filename+"</note>\n")
            sink.write("<note type='input' label='list path, taxonomy information'>"+taxonomy_filename+"</note>\n")
            sink.write("<note type='input' label='spectrum, path'>"+spectra_filename+"</note>\n")
            sink.write("<note type='input' label='protein, taxon'>database</note>\n</bioml>\n")
        self.log.debug('Created [%s]' % input_filename)
        self._iniFile.add_to_ini({'RESULT':self._result_filename})
        self.log.debug("add key 'RESULT' with value [%s] to ini" % self._result_filename)
        return input_filename    
        
        
    def _get_command(self,prefix,input_filename):
        return "cd %s;%s %s" % (self._wd,prefix,input_filename)    
        
    def _validate_run(self,run_code):  
        exit_code = super(Tandem, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code
        stdout = self.stdout.read()            
        if 'Valid models = 0' in stdout:
            self.log.error('No valid model found')
            return 1
        else:
            self.log.debug("more that 0 valid models found") 
        return 0            

if "__main__" == __name__:
    # init the application object (__init__)
    a = Tandem(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)
    
    

        
