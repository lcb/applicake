#!/bin/env python

'''
Created on Nov 11, 2010

@author: quandtan
'''

import cStringIO
import logging
import os
import sys
from argparse import ArgumentParser
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.logger import Logger
from applicake.framework.inihandler import IniHandler
                 
                 
class ApplicationInformation(dict):
    """
    Information about the application object.
    """ 
                   
                 
class Application(object):
    """
    Root class of the framework. 
    Defines the initialization procedure and process logic of every application class 
    that derives from it.      
    """      
    
    def __init__(self, storage='memory',log_level=logging.DEBUG):
        """
        Initialization of variables and basic setup such as the logging mechanism.
        """
        try:                
            # create Application information object and add information        
            self.info = ApplicationInformation()
            self.info['storage'] = storage
            self.info['log_level'] = log_level
            # set name variable to concrete class name if no specific name is provided.
            # the name variable is used to for the logger and file names if the file system is used                      
            argparser = ArgumentParser(description='Applicake application')
            self.define_arguments(parser=argparser) 
            args = self.get_parsed_arguments(parser=argparser)
            self.info.update(args)                                          
            self._init_storage()            
            #    
            #TODO: _validate_parsed_args should contain possibility to change log level 
            #via commandline argument
            #
        except Exception:
            raise
            sys.exit(1)
    
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
        self.log.info('Start [%s]' % self.read_inputs.__name__)
        self.read_inputs()
        self.log.info('Finished [%s]' % self.read_inputs.__name__) 
        self.log.info('Start [%s]' % self.main.__name__)
        exit_code = self.main()
        self.log.info('Finished [%s]' % self.main.__name__)
        self.log.info('Start [%s]' % self.write_outputs.__name__)
        self.write_outputs()
        self.log.info('Finished [%s]' % self.write_outputs.__name__)                
        self.log.info('exit_code [%s]' % exit_code)
        return int(exit_code) 
    
    def _init_storage(self):
        # set file names for stdout/stderr/log if file system is used     
        if self.info['storage'] == 'memory':
            self.out_stream = cStringIO.StringIO()            
#            sys.stdout = self.out_stream
            self.err_stream = cStringIO.StringIO() 
#            sys.stderr = self.err_stream  
            self.log_stream = cStringIO.StringIO()                        
#            self.log = Logger(level=self.info['log_level'],name=self.info['name'],stream=self.log_stream).logger               
        elif self.info['storage'] == 'file':
            self.info['stdout_file'] = ''.join([self.info['name'],".out"])
            self.info['stderr_file'] = ''.join([self.info['name'],".err"]) 
            self.info['log_file'] = ''.join([self.info['name'],".log"])
            # Delete old .out, .err, .log files before initializing the logger
            # this is needed in case an application is executed repeated times in the same directory
            for file in [self.info['stdout_file'],self.info['stderr_file'],self.info['log_file']]:
                if os.path.exists(file):
                    os.remove(file)            
            self.out_stream = open(self.info['stdout_file'], 'a+')            
#            sys.stdout = self.out_stream
            self.err_stream = open(self.info['stderr_file'], 'a+')  
#            sys.stderr = self.err_stream 
            self.log_stream = open(self.info['log_file'],'a+')                         
#            self.log = Logger(level=self.info['log_level'],name=self.info['name'],stream=).logger
#            self.log.debug(os.path.abspath(self.info['log_file']))
        else:
            self.log.critical('storage [%s] is not supported for redirecting streams' % self.info['storage'])
            sys.exit(1)
        sys.stdout = self.out_stream
        sys.stderr = self.err_stream
        self.log = Logger(level=self.info['log_level'],name=self.info['name'],stream=self.log_stream).logger   
                
    
#    def _reset_streams(self):
#        sys.stdout = sys.__stdout__
#        sys.stderr = sys.__stderr__
##    
#    def _redirect_streams(self):                
#        # reset stdout and stderr stream depending on choice of storage
#        if self.info['storage'] == 'memory':
#            self. = cStringIO.StringIO()
#            sys.stdout = self.out_stream
#            self.err_stream = cStringIO.StringIO()
#            sys.stderr = self.std
#        if self.info['storage'] == 'file':
#            stdout = open(self.info['stdout_file'], 'w+')            
#            stderr = open(self.info['stderr_file'], 'w+') 
#        else:
#            self.log.critical('storage [%s] is not supported for redirecting streams' % self.info['storage'])
#            sys.exit(1)
#        sys.stdout = stdout    
#        sys.stderr = stderr
#        print 'hello2'
##        return (orig_stdout,orig_stderr)
    
    def read_inputs(self):
        return 0
    
    def write_outputs(self):
        return 0
                
    def define_arguments(self, parser):        
        """
        Define command line arguments of the application.
        
        Arguments:
        - parser: Object of type ArgumentParser
        """        
        raise NotImplementedError("define_arguments() is not implemented.")   
    
    def get_parsed_arguments(self,parser):
        """
        Parse command line arguments of the application.
        
        Arguments:
        - parser: Object of type ArgumentParser
        
        Return: Dictionary of parsed arguments        
        """
        raise NotImplementedError("get_parsed_arguments() is not implemented.") 
        
                    
    def main(self):
        """
        Contains the main logic of the application.
        
        Return: exit code (integer)
        """  
        
        raise NotImplementedError("main() has not been implemented.") 
        return 0            


class WorkflowNodeApplication(Application):
    """
    The Application type is used to create workflow nodes.

    Return: exit code (integer)    
    """
    
    def define_arguments(self, parser):
        """
        See super class.
        """
        # argument input file: is requred and returns a list if defined multiple times
        parser.add_argument('-i','--input',required=True, dest="inputs", 
                            action='append',help="Input (configuration) file")
        # argument output file: is requred and returns a list if defined multiple times
        parser.add_argument('-o','--output',required=True, dest="outputs",
                            action='append',help="Output (configuration) file")
        parser.add_argument('-n','--name',required=False, dest="name", 
                            default=self.__class__.__name__,
                            help="Name of the workflow node")

    def get_parsed_arguments(self,parser):
        args = vars(parser.parse_args(sys.argv[1:]))
        args['name'] = str(args['name']).lower()
        return args


class WorkflowNodeWrapper(WorkflowNodeApplication):
    """
    The Application type is used to create workflow nodes that 
    prepare, run and validate the execution of an external application.
    
    Return: exit code (integer) 
    """
    
    def define_arguments(self,parser):
        """
        See super class.
        """
        super(WorkflowNodeWrapper, self).define_arguments(parser=parser)
        parser.add_argument('-p','--prefix',required=True, dest="prefix",
                            help="Prefix of the command to execute")      
        parser.add_argument('-t','--template',required=False, dest="template", 
                            default=self.__class__.__name__,
                            help="Name of the workflow node")               
    
    def main(self):
        """
        Prepare, run and validate the execution of an external program.
        
        Return: exit code (integer) 
        """
        self.log.info('Start [%s]' % self.prepare_run.__name__)
        command = self.prepare_run(prefix=self.info['prefix'])     
        self.log.info('Finish [%s]' % self.prepare_run.__name__)
        if command is not None:
            # necessary when e.g. the template file contains '\n' what will cause problems 
            # when using concatenated shell commands
            self.log.debug('remove all [\\n] from command string')
            command  = command.replace('\n','')   
            self.log.info('Command [%s]' % str(command))
        self.log.info('Start [%s]' % self._run.__name__)
        run_code = self._run(command)
        self.log.info('Finish [%s]' % self._run.__name__)
        self.log.info('run_code [%s]' % run_code)        
        self.log.info('Start [%s]' % self.validate_run.__name__)
        exit_code = self.validate_run(run_code=run_code)
        self.log.debug('exit code [%s]' % exit_code)
        self.log.info('Finish [%s]' % self.validate_run.__name__)        
        return exit_code

    def prepare_run(self,prefix):
        """
        Prepare the execution of an external application.
        
        Return: String containing the command to execute.
        """
        raise NotImplementedError("prepare_run() is not implemented") 
        command = None
        return command

    def _run(self,command):
        """
        Execute a command and collects it's output in self.out_stream and self.err_stream 
        The stdout and stderr are written to files if file system should be used.
        Otherwise stdout and stderr of the application are separately printed to 
        stdout because the logger uses by default the stderr.
        
        Return: return code (integer).
        This is eigher 1 or the original return code of the executed command.
        """
        # when the command does not exist, process just dies.therefore a try/catch is needed          
        try:     
            if self.info['use_filesystem']:
                self.out_stream = open(self._stdout_filename, 'w+')
                self.err_stream = open(self._stderr_filename, 'w+')                        
                p = Popen(command, shell=True, stdout=self.out_stream, stderr=self.err_stream)
                p.wait()
            else:
                p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
                output, error = p.communicate()                                                                                                                                                                            
                self.out_stream = cStringIO.StringIO(output)
                self.err_stream = cStringIO.StringIO(error)
                # prints 
                print("=== stdout ===")
                print(self.out_stream.read())
                print("=== stderr ===")  
                print(self.err_stream.read()) 
            # set pointer back to 1st character. 
            # therefore, fh has not to be closed (and opened again in validate_run ()
            self.out_stream.seek(0)
            self.err_stream.seek(0)   
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
    
    