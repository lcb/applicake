#!/bin/env python

'''
Created on Nov 11, 2010

@author: quandtan
'''

import sys
import getopt
import logging
import os
import cStringIO
import argparse
import glob
import shutil
import traceback
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.logger import Logger
from applicake.framework.inihandler import IniHandler
from applicake.utils import Workflow
from applicake.utils import Utilities
                 
class Application(object):
    """
    Root class of the framework. 
    Defines the initialization procedure and process logic of every application class that derives from it.      
    """      
    
    def __init__(self, use_filesystem=True,log_level=logging.DEBUG,name=None):
        """
        Initialization of variables and basic setup such as the logging mechanism.
        """
        # set name variable to concrete class name if no specific name is provided.
        # the name variable is used to for the logger and file names if the file system is used
        self.name= name.lower() if name else str(self.__class__.__name__).lower()                        
        # set file names for stdout/stderr/log if file system is used
        if use_filesystem:
            self.stdout_filename = ''.join([self.name,".out"])
            self.stderr_filename = ''.join([self.name,".err"]) 
            log_filename = ''.join([self.name,".log"])
            # Delete old .out, .err, .log files before initializing the logger
            # this is needed in case an application is executed repeated times.
            files = [log_filename,self.stdout_filename,self.stderr_filename]
            for file in files:
                if os.path.exists(file):
                    os.remove(file) 
            self.log = Logger(level=log_level,name=self.name,file=self._log_filename).logger
            self.log.debug(os.path.abspath(self._log_filename))
        # initializes only the logger if no file system is used
        else:
            self.log = Logger(level=self._log_level).logger  
        #    
        #TODO: _validate_parsed_args should contain possibility to change log level via commandline argument
        #
    
    def __call__(self, args):
        """
        Program logic of the Application class.
        First, the command line arguments are parsed and validated. 
        Then, the main program logic is executed.
        
        Return: exit code (integer)
        """      
        self.log.debug('application class file [%s]' % args[0])
        self.log.debug('arguments [%s]' % args[1:])
        self.log.debug('Python class [%s]' % self.__class__.__name__)   
        self.log.info('Start [%s]' % self._get_parsed_args.__name__)
        parsed_args = self._get_parsed_args(args[1:])        
        self.log.info('Finish [%s]' % self._get_parsed_args.__name__)          
        self.log.info('Start [%s]' % self._validate_parsed_args.__name__)
        self._validate_parsed_args(parsed_args)        
        self.log.info('Finish [%s]' % self._validate_parsed_args.__name__)
        self.log.info('Start [%s]' % self._main.__name__)
        exit_code = self.main()
        self.log.info('Finished [%s]' % self._main.__name__)              
        self.log.info('exit_code [%s]' % exit_code)
        return int(exit_code)  
        
    def main(self):
        """
        Contains the main logic of the application.
        
        Return: exit code (integer)
        """  
        raise NotImplementedError("main() has not been implemented.") 
        return 0
                
    def get_parsed_args(self,args):        
        """
        Parse command line arguments and returns dictionary with according key/value pairs
        """
        # need to pass args as otherwise sys.argv is used and this complicates this for the collector
        raise NotImplementedError("get_parsed_args() is not implemented.")               


class WorkflowNodeApplication(Application):
    def get_argument_parser(self):
        return None


class WorkflowNodeWrapper(WorkflowNodeApplication):
    """
    Wrapper that prepare, run and validate the execution of an external application.
    
    Return: exit code (integer) 
    """
    
    def main(self):
        """
        Prepare, run and validate the execution of an external program.
        
        Return: exit code (integer) 
        """
        self.log.info('Start [%s]' % self._preprocessing.__name__)
        command = self.prepare_run()     
        self.log.info('Finish [%s]' % self._preprocessing.__name__)
        if command is not None:
            #necessary when e.g. the template file contains '\n' what will cause problems when using concatenated shell commands
            self.log.debug('remove all [\\n] from command string')
            command  = command.replace('\n','')   
            self.log.info('Command [%s]' % str(command))
        self.log.info('Start [%s]' % self._run.__name__)
        run_code = self._run(command)
        self.log.info('Finish [%s]' % self._run.__name__)
        self.log.info('run_code [%s]' % run_code)        
        self.log.info('Start [%s]' % self._validate_run.__name__)
        exit_code = self.validate_run(run_code)
        self.log.debug('exit code [%s]' % exit_code)
        self.log.info('Finish [%s]' % self._validate_run.__name__)        
        return exit_code

    def prepare_run(self):
        """
        Prepare the execution of an external application.
        
        Return: String containing the command to execute.
        """
        raise NotImplementedError("prepare_run() is not implemented") 
        command = None
        return command

    def _run(self,command):
        """
        Execute a command and collects it's output in self.stdout and self.stderr 
        The stdout and stderr are written to files if file system should be used.
        Otherwise stdout and stderr of the application are separately printed to 
        stdout because the logger uses by default the stderr.
        
        Return: return code (integer).
        This is eigher 1 or the original return code of the executed command.
        """
        # when the command does not exist, process just dies.therefore a try/catch is needed          
        try:     
            if self._use_filesystem:
                self.stdout = open(self._stdout_filename, 'w+')
                self.stderr = open(self._stderr_filename, 'w+')                        
                p = Popen(command, shell=True, stdout=self.stdout, stderr=self.stderr)
                p.wait()
            else:
                p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
                output, error = p.communicate()                                                                                                                                                                            
                self.stdout = cStringIO.StringIO(output)
                self.stderr = cStringIO.StringIO(error)
                # prints 
                print("=== stdout ===")
                print(self.stdout.read())
                print("=== stderr ===")  
                print(self.stderr.read()) 
            # set pointer back to 1st character. 
            # therefore, fh has not to be closed (and opened again in validate_run ()
            self.stdout.seek(0)
            self.stderr.seek(0)   
            # return exit code of the command line execution                             
            return p.returncode                       
        except Exception,e:
            self.log.exception(e)
            return 1 
    
    def validate_run(self,run_code):
        """
        Validate the results of the _run() and return [0] if proper succeeded.
        
        Return: exit_code (integer). 
        This is either the original return_code of external application or 
        a developer-specific value.
        """  
        raise NotImplementedError("validate_run() is not implemented") 
        exit_code = run_code
        return exit_code
    
    