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

class TppCollector(CollectorApplication):
    '''
    classdocs
    '''
    def _run(self,ini_filenames):        
        for filename in ini_filenames:
            self.log.debug('ini file to process [%s]' % filename)
            exit_code = 0
            a = InterProphet(use_filesystem=True,name=None)
            exit_code = a([' ','-p','InterProphetParser','-i',filename,'-t',self._template_filenames[0],'-o',filename])
            if exit_code == 0:
                self.log.debug('prog [%s] with finished with exit_code [%s]' % (a.name,exit_code))
                self.log.debug('content of the log file: [\n%s\n]' % open(a._log_filename,'r').read())
                #copy the log file to the working dir
                for fn in [a._log_filename,a._stderr_filename,a._stdout_filename]:
                    shutil.move(fn, os.path.join(a._wd,fn))                 
                a = PepXML2CSV(use_filesystem=True,name=None)
                exit_code = a([' ','-p','pepxml2csv','-p','fdr2probability','-i',filename,'-t',self._template_filenames[1],'-o',filename])
            if exit_code == 0:
                self.log.debug('prog [%s] with finished with exit_code [%s]' % (a.name,exit_code))
                self.log.debug('content of the log file: [\n%s\n]' % open(a._log_filename,'r').read())
                #copy the log file to the working dir
                for fn in [a._log_filename,a._stderr_filename,a._stdout_filename]:
                    shutil.move(fn, os.path.join(a._wd,fn))  
                a = ProteinProphet(use_filesystem=True,name=None)
                exit_code = a([' ','-p','ProteinProphet','-i',filename,'-t',self._template_filenames[2],'-o',filename])
            if exit_code == 0:
                self.log.debug('prog [%s] with finished with exit_code [%s]' % (a.name,exit_code))
                self.log.debug('content of the log file: [\n%s\n]' % open(a._log_filename,'r').read())
                #copy the log file to the working dir
                for fn in [a._log_filename,a._stderr_filename,a._stdout_filename]:
                    shutil.move(fn, os.path.join(a._wd,fn))                     
                a = OpenbisExport(use_filesystem=True,name=None)
                exit_code = a([' ','-p','ProteinProphet','-i',filename,'-t',self._template_filenames[2],'-o',filename])
            if exit_code == 0:
                self.log.debug('prog [%s] with finished with exit_code [%s]' % (a.name,exit_code))
                self.log.debug('content of the log file: [\n%s\n]' % open(a._log_filename,'r').read())
                #copy the log file to the working dir
                for fn in [a._log_filename,a._stderr_filename,a._stdout_filename]:
                    shutil.move(fn, os.path.join(a._wd,fn))                        
            if exit_code != 0:
                return exit_code        
                    
                                   
            
#            progs = []
#            progs.append(InterProphet(use_filesystem=True,name=None))
#            progs.append(PepXML2CSV(use_filesystem=True,name=None))
#            progs.append(ProteinProphet(use_filesystem=True,name=None))
#            progs.append(OpenbisExport(use_filesystem=True,name=None))
#            if len(progs) == len(self._template_filenames):
#                self.log.debug('number of progs and templates is the same [%s]' % len(progs))
#            else:
#                self.log.error('number of progs [%s] does not match number of templates [%s]' % (len(progs),len(self._template_filenames)) )
#                return 1
#            args = []
#            args.append([' ','-p','InterProphetParser','-i',filename,'-t',self._template_filenames[0],'-o',filename])
#            args.append([' ','-p','pepxml2csv','-p','fdr2probability','-i',filename,'-t',self._template_filenames[1],'-o',filename])
#            args.append([' ','-p','ProteinProphet','-i',filename,'-t',self._template_filenames[2],'-o',filename])
#            args.append([' ','-p','protxml2spectralcount','-p','protxml2openbis','-i',filename,'-t',self._template_filenames[3],'-o',filename])            
#            if len(progs) == len(args):
#                self.log.debug('number of progs and args is the same [%s]' % len(progs))
#            else:
#                self.log.error('number of progs [%s] does not match number of args [%s]' % (len(progs),len(args)) )
#                return 1
#            for j,prog in enumerate(progs):
#                exit_code = prog(args[j])
#                self.log.debug('prog [%s] with num [%s] finished with exit_code [%s]' % (prog.name,j,exit_code))
#                self.log.debug('content of the log file: [\n%s\n]' % open(prog._log_filename,'r').read())
#                #copy the log file to the working dir
#                for fn in [prog._log_filename,prog._stderr_filename,prog._stdout_filename]:
#                    shutil.move(fn, os.path.join(prog._wd,fn))                
#                if exit_code != 0:
#                    return exit_code                
                      
    def _validate_parsed_args(self,dict):
        self._input_filenames = dict['input_filenames']
        self._template_filenames = dict['template_filenames']        
        super(TppCollector, self)._validate_parsed_args(dict)
        

if "__main__" == __name__:
    # init the application object (__init__)
    a = TppCollector(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)