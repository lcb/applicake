#!/usr/bin/env python
'''
Created on Nov 17, 2010

@author: quandtan
'''
import sys,os
import shutil
from applicake.app import SpectraIdentificationApplication
from applicake.utils import Utilities,IniFile

class Tandem(SpectraIdentificationApplication):
    
    def _create_input_files(self,config):
        default_filename = os.path.join(self._wd,'default.params' )            
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,out_filename=default_filename)
        self.log.debug('Created [%s]' % default_filename)
        taxonomy_filename = os.path.join(self._wd,'taxonomy.params')
        db_filename = None
        spectra_filename = None        
        try:
            db_filename = config['DBASE']
            spectra_filename = config['SPECTRA']
            (dir,name) = os.path.split(spectra_filename)
            (basename,ext) = os.path.splitext(name)
        except Exception,e:
            self.log.exception(e)
            sys.exit(1)           
        with open(taxonomy_filename, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write('<bioml>\n<taxon label="database">')
            sink.write('<file format="peptide" URL="%s"/>' % db_filename)
            sink.write("</taxon>\n</bioml>")
        self.log.debug('Created [%s]' % taxonomy_filename)
        self._run_filename = os.path.join(self._wd,'run.params' )
        (dir,filename) = os.path.split(self.output_filename)
        if dir is None:
             self.output_filename = os.path.join(self._wd,self.output_filename)       
        with open(self._run_filename, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write("<bioml>\n<note type='input' label='list path, default parameters'>"+default_filename+"</note>\n")
            sink.write("<note type='input' label='output, xsl path' />\n<note type='input' label='output, path'>"+self._output_filename+"</note>\n")
            sink.write("<note type='input' label='list path, taxonomy information'>"+taxonomy_filename+"</note>\n")
            sink.write("<note type='input' label='spectrum, path'>"+spectra_filename+"</note>\n")
            sink.write("<note type='input' label='protein, taxon'>database</note>\n</bioml>\n")
        self.log.debug('Created [%s]' % self._run_filename)
        
    
    
    def _preprocessing(self):
        self.log.debug('Read ini file [%s]' % os.path.abspath(self._input_filename))
        config = IniFile(in_filename=self._input_filename).read_ini()                
        self.log.debug(config)
        self.log.debug('Start %s' % self.create_workdir.__name__)
        self._wd = self.create_workdir(config)
        self.log.debug('Finished %s' % self.create_workdir.__name__) 
        self.log.debug('Start %s' % self._create_input_files.__name__)
        run_filename = self._create_input_files(config)
        self.log.debug('Finished %s' % self._create_input_files.__name__)                
        return "cd %s;%s %s" % (self._wd,self._command_prefix,self._run_filename)
        
    def _validate_run(self,run_code):        
        if 0 < run_code:
            return run_code 
        if not os.path.exists(self.output_filename):
            self.log.error('File [%s] does not exist' % os.path.abspath(self.output_filename))
            return 1
        else:
            self.log.debug('File [%s] does exist' % os.path.abspath(self.output_filename))
        stdout = self.stdout.read()            
        if 'Valid models = 0' in stdout:
            self.log.error('No valid model found')
            return 1
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
    
    

        
