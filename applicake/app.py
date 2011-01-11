#!/bin/env python

'''
Created on Nov 11, 2010

@author: quandtan
'''

import sys,getopt,logging,os,cStringIO,argparse
from subprocess import Popen, PIPE
from applicake.utils import Logger as logger
from applicake.utils import IniFile

                 
class Application():
    'Application class to prepare and verify the execution of external programs'      
        
    def __call__(self, args):
        "Running the class' main logic and returns the exit code of the validate_run method"      
        self.log.debug('application class file [%s]' % args[0])
        self.log.debug('arguments [%s]' % args[1:])
        self.log.debug('Python class [%s]' % self.__class__.__name__)   
        self.log.info('Start [%s]' % self._get_parsed_args.__name__)
        parsed_args = self._get_parsed_args()        
        self.log.info('Finish [%s]' % self._get_parsed_args.__name__)          
        self.log.info('Start [%s]' % self._validate_parsed_args.__name__)
        self._validate_parsed_args(parsed_args)        
        self.log.info('Finish [%s]' % self._validate_parsed_args.__name__)              
        self.log.info('Start [%s]' % self._preprocessing.__name__)
        command = self._preprocessing()        
        self.log.info('Finish [%s]' % self._preprocessing.__name__)
        if command is not None:
            self.log.info('Command [%s]' % str(command))
        self.log.info('Start [%s]' % self._run.__name__)
        run_code = self._run(command)
        self.log.info('Finish [%s]' % self._run.__name__)
        if run_code is not None:
            self.log.info('run_code [%s]' % run_code)        
        self.log.info('Start [%s]' % self._validate_run.__name__)
        exit_code = self._validate_run(run_code)
        self.log.info('Finish [%s]' % self._validate_run.__name__)
        self.log.info('exit_code [%s]' % exit_code)
        return exit_code
    
    def __init__(self, use_filesystem=True,log_level=logging.DEBUG,name=None):
        'Initialization of variables and basic preparation of running the class'
        if name is None:
            name = self.__class__.__name__
        self.name=name  
        self._stdout_filename = ''.join([self.name,".out"])
        self._stderr_filename = ''.join([self.name,".err"]) 
        self._log_filename = ''.join([self.name,".log"])
        self._use_filesystem = use_filesystem
        self._log_level = log_level                    
        self._clean_up()
        if use_filesystem:
            self.log = logger(level=self._log_level,file=self._log_filename).logger
        else:
            self.log = logger(level=self._log_level).logger  
            
        #TODO: _validate_parsed_args should contain possibility to change log level via commandline argument
                  
    def _clean_up(self):
        'Delete old .out, .err, .log files before initializing the logger'
        files = [self._log_filename,self._stdout_filename,self._stderr_filename]
        for file in files:
            if os.path.exists(file):
                os.remove(file) 
                
    def _get_parsed_args(self):
        '''
        Parse command line arguments and returns dictionary with according key/value pairs
        '''
        raise NotImplementedError("Called '_get_parsed_args' method on abstact class")               
                    
    def _run(self,command=None):
        '''
        Exectes the main part of the Application.
        When a external application is executed, the optional parameter command can be passed to this method.
        the 'command' can be produced by the _preprocessing() 
        Also, when an external application is executed, it should return the original return code of that application.
        '''
        raise NotImplementedError("Called '_run' method on abstract class")          
        

    def _preprocessing(self):
        '''
        Prepare running the main part of the application. 
        When an external application is executed it should return the command to execute
        '''
        raise NotImplementedError("Called '_preprocessing' method on abstract class") 

    def _validate_parsed_args(self,dict=None):
        '''
        Validate the parsed command line arguments.
        '''
        raise NotImplementedError("Called '_validate_parsed_args' method on abstact class")

    def _validate_run(self,run_code=None):
        '''
        Validate the results of the _run() and return [0] if proper succeeded.
        The optional parameter run_code can be passed e.g. when the _run() executed an external application.
        '''
        raise NotImplementedError("Called '_validate_run' method on abstact class")


class ExternalApplication(Application):
    'Simple application that executes an external program'
    
    def _get_parsed_args(self):
        parser = argparse.ArgumentParser(description='A simple application to call external programs')
        parser.add_argument('-p','--prefix', action="store", dest="p",type=str,help="prefix of the command to execute")
        a = parser.parse_args()
        return {'prefix':a.p} 
        
    
    def _preprocessing(self):
        return self._command
    
    def _run(self,command=None):
        'Run and monitor the external application. Returns 1 or the original return code of that application'         
        # when the command does not exist, process just dies.therefore a try/catch is needed          
        try:     
            if self._use_filesystem:
                self.stdout = open(self._stdout_filename, 'w+')
                self.stderr = open(self._stderr_filename, 'w+')                        
                p = Popen(command, shell=True, stdout=self.stdout, stderr=self.stderr)
                p.wait()
                #set pointer back to 1st character. therefore, fh has not to be closed (and opened again in validate_run ()
                self.stdout.seek(0)
                self.stderr.seek(0)                                
                return p.returncode                       
            else:
                p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
                output, error = p.communicate()                                                                                                                                                                            
                self.stdout = cStringIO.StringIO(output)
                self.stderr = cStringIO.StringIO(error)
                stdout = self.stdout.read()
                stderr = self.stderr.read()
                print("=== stdout ===")
                print(stdout)
                print("=== stderr ===")  
                print(stderr) 
                return p.returncode  
        except Exception,e:
            self.log.exception(e)
            return 1     
    
    def _validate_parsed_args(self,dict):    
        self._command = dict['prefix']            
        
    def _validate_run(self,run_code):
        print("=== stdout ===")
        print(self.stdout.read())
        print("=== stderr ===")  
        print(self.stderr.read())   
        return run_code        

class WorkflowApplication(ExternalApplication):
    
    def _get_app_inputfilename(self):
        raise NotImplementedError("Called '_create_app_inputfiles' method on abstact class")
    
    def _get_command(self,prefix,input_filename):
        raise NotImplementedError("Called '_get_command' method on abstact class")     
    
    def _get_parsed_args(self):
        parser = argparse.ArgumentParser(description='Wrapper around a spectra identification application')
        parser.add_argument('-p','--prefix', action="store", dest="prefix",type=str,help="prefix of the command to execute")
        parser.add_argument('-i','--input', action="store", dest="input_filename",type=str,help="input file")
        parser.add_argument('-o','--output', action="store", dest="output_filename",type=str,help="output file")
        a = parser.parse_args()
        return {'prefix':a.prefix,'input_filename':a.input_filename,'output_filename':a.output_filename}      
    
    def _preprocessing(self):
        self.log.debug('Read input file [%s]' % os.path.abspath(self._input_filename))
        self._iniFile = IniFile(input_filename=self._input_filename,output_filename=self._output_filename)
        config = self._iniFile.read_ini()                
        self.log.debug("content: %s" % config)
        self.log.info('Start %s' % self.create_workdir.__name__)
        self._wd = self.create_workdir(config)
        self.log.info('Finished %s' % self.create_workdir.__name__) 
        self.log.info('Start %s' % self._get_app_inputfilename.__name__)
        app_input_filename = self._get_app_inputfilename(config)
        self.log.info('Finished %s' % self._get_app_inputfilename.__name__)                
        return self._get_command(prefix=self._command_prefix,input_filename=app_input_filename)   
    
    def _validate_parsed_args(self,dict):     
        if dict['prefix'] is None:
            self.log.fatal('argument [prefix] was not set')
            sys.exit(1)
        else:
            self._command_prefix = dict['prefix']
        if dict['input_filename'] is None:
            self.log.fatal('argument [input] was not set')
            sys.exit(1)
        else:
            self._input_filename = dict['input_filename']
            self.log.debug("input file [%s]" % os.path.abspath(self._input_filename))
            if not os.path.exists(self._input_filename):
                self.log.fatal('file [%s] does not exist' % self._input_filename)
        if dict['output_filename'] is None:
            self.log.fatal('cli argument [output] was not set')
            sys.exit(1)
        else:
            self._output_filename = dict['output_filename']                                  
                
    def create_workdir(self,config):
        basedir = None  
        try:
            basedir = config['DIR'] 
            param_idx = config['PARAM_IDX']
            spectra_idx =  config['SPECTRA_IDX']
            wd = os.path.join(basedir,param_idx)
            wd = os.path.join(wd,spectra_idx)
            wd = os.path.join(wd,self.name)                       
            os.makedirs(wd)
            self.log.debug('Created workdir [%s]' % wd)
        except Exception,e:
            self.log.exception(e)  
            sys.exit(1)
        return wd          
                            
                            
class SpectraIdentificationApplication(WorkflowApplication):   
    
    def _get_parsed_args(self):
        parser = argparse.ArgumentParser(description='Wrapper around a spectra identification application')
        parser.add_argument('-p','--prefix', action="store", dest="prefix",type=str,help="prefix of the command to execute")
        parser.add_argument('-i','--input', action="store", dest="input_filename",type=str,help="input file")
        parser.add_argument('-t','--template', action="store", dest="template_filename",type=str,help="template of the program specific input file")
        parser.add_argument('-o','--output', action="store", dest="output_filename",type=str,help="output file")
#        parser.add_argument('-b', action="store_true", dest='2', default=False,help='test of a boolean')
#        parser.add_argument('-i', action="store", dest="3", default=0, type=int,help='test of a integer')
        a = parser.parse_args()
        return {'prefix':a.prefix,'input_filename':a.input_filename,'template_filename':a.template_filename,'output_filename':a.output_filename}         

    def _validate_parsed_args(self,dict):     
        if dict['prefix'] is None:
            self.log.fatal('argument [prefix] was not set')
            sys.exit(1)
        else:
            self._command_prefix = dict['prefix']
        if dict['input_filename'] is None:
            self.log.fatal('argument [input] was not set')
            sys.exit(1)
        else:
            self._input_filename = dict['input_filename']
            self.log.debug("input file [%s]" % os.path.abspath(self._input_filename))
            if not os.path.exists(self._input_filename):
                self.log.fatal('file [%s] does not exist' % self._input_filename)
        if dict['template_filename'] is None:
            self.log.fatal('cli argument [template] was not set')
            sys.exit(1)
        else:
            self._template_filename = dict['template_filename']
            self.log.debug("template file [%s]" % os.path.abspath(self._template_filename))
            if not os.path.exists(self._template_filename):
                self.log.fatal('file [%s] does not exist' % self._template_filename)
                sys.exit(1)
        if dict['output_filename'] is None:
            self.log.fatal('cli argument [output] was not set')
            sys.exit(1)
        else:
            self._output_filename = dict['output_filename']           
                   
      
        