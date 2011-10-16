#!/usr/bin/env python
'''
Created on Jan 26, 2011

@author: quandtan
'''
import os,sys,shutil
from applicake.app import CollectorApplication
from applicake.interprophet import InterProphet
from applicake.pepxml2csv import PepXML2CSV
from applicake.proteinprophet import ProteinProphet
from applicake.openbisexport import OpenbisExport
from applicake.utils import ThreadPool

class TppCollector(CollectorApplication):
    '''
    classdocs
    '''
    #!!! exit_code - strategy is not fail safe here!!!!
    def _sequence(self, filename,idx):
        if self._exit_code != 0:
            self.log.error('file [%s] was not processed because a previous file was processed with errors.' % filename)
            return 
        self.log.debug('ini file to process [%s]' % filename)
        prog = InterProphet(use_filesystem=True, name="%s-%s" % (idx,'iprophet'), log_console=False)
        self._exit_code = prog(['interprophet.py', '-p', 'InterProphetParser', '-i', filename, '-t', self._template_filenames[0], '-o', filename])
        self.log.debug('[%s]: prog [%s] finished with exit_code [%s]' % (filename,prog.name, self._exit_code))
        for fn in [prog._log_filename, prog._stderr_filename, prog._stdout_filename]:
            src = os.path.abspath(fn)
            dest = os.path.join(prog._wd, fn)
            try: shutil.move(src, dest)
            except: self.log.error("Error moving [%s] to [%s]" % (src,dest))
        if self._exit_code == 0:                         
            prog = PepXML2CSV(use_filesystem=True, name="%s-%s" % (idx,'pepxml2csv'), log_console=False)
            self._exit_code = prog(['pepxml2csv.py', '--prefix=pepxml2csv', '--prefix=fdr2probability.py', '--input=' + filename, '--template=' + self._template_filenames[1], '--output=' + filename])
#            self._exit_code = prog(['pepxml2csv.py', '--prefix=pepxml2csv', '--prefix=fdr2probability', '--input=' + filename, '--template=' + self._template_filenames[1], '--output=' + filename])
            self.log.debug('prog [%s] finished with exit_code [%s]' % (prog.name, self._exit_code))
            for fn in [prog._log_filename, prog._stderr_filename, prog._stdout_filename]:
                src = os.path.abspath(fn)
                dest = os.path.join(prog._wd, fn)
                try: shutil.move(src, dest)
                except: self.log.error("Error moving [%s] to [%s]" % (src,dest))
        if self._exit_code == 0:                 
            prog = ProteinProphet(use_filesystem=True, name="%s-%s" % (idx,'proteinprophet'), log_console=False)
            self._exit_code = prog(['proteinprophet.py', '--prefix=ProteinProphet', '--input=' + filename, '--template=' + self._template_filenames[2], '--output=' + filename])
            self.log.debug('prog [%s] finished with exit_code [%s]' % (prog.name, self._exit_code))
            for fn in [prog._log_filename, prog._stderr_filename, prog._stdout_filename]:
                src = os.path.abspath(fn)
                dest = os.path.join(prog._wd, fn)
                try: shutil.move(src, dest)
                except: self.log.error("Error moving [%s] to [%s]" % (src,dest))
        if self._exit_code == 0:                 
            prog = OpenbisExport(use_filesystem=True, name="%s-%s" % (idx,'openbisexport'), log_console=False)
            self._exit_code = prog(['openbisexport.py', '--prefix=protxml2spectralcount','--prefix=protxml2modifications', '--prefix=protxml2openbis', '--input=' + filename, '--template=' + self._template_filenames[3], '--output=' + filename])
#                print ("[%s] [%s]: %s" %(os.path.split(filename)[1],3,exit_code))
            self.log.debug('prog [%s] with finished with exit_code [%s]' % (prog.name, self._exit_code))
            for fn in [prog._log_filename, prog._stderr_filename, prog._stdout_filename]:
                src = os.path.abspath(fn)
                dest = os.path.join(prog._wd, fn)
                try: shutil.move(src, dest)
                except: self.log.error("Error moving [%s] to [%s]" % (src,dest))
        if self._exit_code == 0:             
            self.log.debug('finished collector job for [%s] successfully.' % filename)            
        else:
            self.log.error('[%s]: content of the log file[%s]: [\n%s\n]' % (prog._log_filename, open(prog._log_filename, 'r').read()))
#            self._exit_code = exit_code
            sys.exit(1)

    def _run(self,ini_filenames):   
        self._exit_code = 0
        pool = ThreadPool(self._num_threads)        
        for i,e in enumerate(ini_filenames):            
            pool.add_task(self._sequence, e,i)
        pool.wait_completion()             
        return self._exit_code          
      
    
    def _validate_run(self,run_code):              
        return run_code       
                         

if "__main__" == __name__:
    # init the application object (__init__)
    a = TppCollector(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename]:
        if os.path.exists(filename):
            shutil.move(filename, os.path.join(a._wd,filename))
        else:
            sys.stdout.write('file does not exit [%s] and was therefore not moved to [%s]\n' % (filename,os.path.join(a._wd,filename)) )
    print(exit_code)
    
#    sys.exit(1)
    sys.exit(exit_code)   
    