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
from applicake.framework.confighandler import ConfigHandler
                 
                 
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
    
    def __init__(self):
        """
        Basic setup of the Application class        
        such as argument parsing and initialization of streams        
        """
        try:                
            # create Application information object and add information        
            self.info = ApplicationInformation()
            # set name variable to concrete class name if no specific name is provided.
            # the name variable is used to for the logger and file names if the file system is used                      
            argparser = ArgumentParser(description='Applicake application')
            self.define_arguments(parser=argparser) 
            args = self.get_parsed_arguments(parser=argparser)
            self.info.update(args)                                        
            self._init_streams() 
            self.config = {}
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
        self.log.info('Start [%s]' % self.read_input_files.__name__)
        self.read_input_files()
        self.log.info('Finished [%s]' % self.read_input_files.__name__)                         
        self.log.info('Start [%s]' % self.main.__name__)
        exit_code = self.main()
        self.log.info('Finished [%s]' % self.main.__name__)               
        self.log.info('Start [%s]' % self.write_output_files.__name__)
        self.write_output_files()
        self.log.info('Finished [%s]' % self.write_output_files.__name__)         
        self.log.info('exit_code [%s]' % exit_code)
        return int(exit_code)   
    
    def __del__(self):
        """
        Reset streams to their original
        
        If storage='memory' is used, out and err stream are printed to stdout
        and log stream is printed to stderr        
        """
        self.reset_streams()   
        if self.info['storage'] == 'memory':
            print '=== stdout ==='
            self.out_stream.seek(0)
            for line in self.out_stream.readlines():
                print line
            print '=== stderr ==='
            self.err_stream.seek(0)
            for line in self.err_stream.readlines():
                print line
            self.log_stream.seek(0)                
            for line in self.log_stream.readlines():
                sys.stderr.write(line)                 

    def _init_streams(self):
        """
        Initializes the streams for stdout/stderr/log
        """     
        if self.info['storage'] == 'memory':
            self.out_stream = cStringIO.StringIO()            
            self.err_stream = cStringIO.StringIO() 
            self.log_stream = cStringIO.StringIO()                                       
        elif self.info['storage'] == 'file':
            self.info['out_file'] = ''.join([self.info['name'],".out"])
            self.info['err_file'] = ''.join([self.info['name'],".err"]) 
            self.info['log_file'] = ''.join([self.info['name'],".log"])
            # streams are initialized with 'w+' that files are pured first before
            # writing into them         
            self.out_stream = open(self.info['out_file'], 'w+')            
            self.err_stream = open(self.info['err_file'], 'w+')  
            self.log_stream = open(self.info['log_file'],'w+')                         
        else:
            self.log.critical('storage [%s] is not supported for redirecting streams' % self.info['storage'])
            sys.exit(1)
        # redirect/set streams    
        sys.stdout = self.out_stream
        sys.stderr = self.err_stream
        self.log = Logger(level=self.info['log_level'],name=self.info['name'],stream=self.log_stream).logger                                          
        
    def check_files(self,files):
        for fin in files:
            fail1 = not os.path.exists(fin)
            fail2 = not os.path.isfile(fin)
            fail3 = not os.access(fin,os.R_OK)
            fail4 = not (os.path.getsize(fin) > 0)
            fails = [fail1,fail2,fail3,fail4]
            if any(fails):
                msg = '''file [%s] does not exist [%s], 
                is not a file [%s], cannot be read [%s] or
                has no file larger that > 0kb [%s]''' % (
                                                                os.path.abspath(fin),
                                                                fail1,fail2,fail3,fail4
                                                                )
                self.log.critical(msg)
                sys.exit(1)
            self.log.debug('file [%s] checked successfully' % fin)        
                
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
    
    def read_input_files(self):
        """
        Read and verifies input files passed defines by command line argument(s) 
        """    
        key = 'inputs'
        if not self.info.has_key(key):
            self.log.critical('could not find key [%s] in application info [%s]' % (key,self.info) )
            sys.exit(1)
        inputs = self.info[key]
        self.check_files(inputs)
        for f in inputs:      
            config = ConfigHandler().read(f)  
            self.log.debug('file [%s], content [\n%s\n]' % (f,config))   
            self.config = ConfigHandler().append(self.config, config)
            self.log.debug('config after appending: [%s]' % self.config)
            
    def reset_streams(self):
        """
        Reset the stdout/stderr to their original
        """
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__                                                             
    
    def write_output_files(self): 
        files = [self.info['output']]
        for f in files: 
            self.log.debug('output file [%s]' % f)                  
            ConfigHandler().write(self.config, f) 
        self.check_files(files)    


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
        parser.add_argument('-i','--input',required=True,dest="inputs", 
                            action='append',help="Input (configuration) file(s)")
        # argument output file: is requred and returns a list if defined multiple times
        parser.add_argument('-o','--output',required=True, nargs=1, dest="output",
                            action='store',help="Output (configuration) file")
        parser.add_argument('-n','--name',required=False, nargs=1, dest="name", 
                            default=self.__class__.__name__,
                            help="Name of the workflow node")
        parser.add_argument('-s','--storage',required=False, nargs=1, dest="storage", 
                            default=None,choices=['memory','file'],
                            help="Storage type for produced streams")  
        parser.add_argument('-l','--loglevel',required=False, nargs=1, dest="log_level", 
                            default=None,choices=['DEBUG','INFO','WARNING',
                                                  'ERROR','CRITICAL'],
                            help="Storage type for produced streams")        

    def get_parsed_arguments(self,parser):
        args = vars(parser.parse_args(sys.argv[1:]))
        args['name'] = str(args['name'][0]).lower()
        args['output'] = args['output'][0]
        args['storage'] = args['storage'][0]
        args['log_level'] = args['log_level'][0]
        return args


class WorkflowNodeWrapper(WorkflowNodeApplication):
    """
    The Application type is used to create workflow nodes that 
    prepare, run and validate the execution of an external application.
    
    Return: exit code (integer) 
    """
    
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
            if self.info['storage'] == 'memory':
                p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
                output, error = p.communicate()                                                                                                                                                                            
                self.out_stream = cStringIO.StringIO(output)
                self.err_stream = cStringIO.StringIO(error)  
            elif self.info['storage'] == 'file':
                p = Popen(command, shell=True,stdout=sys.stdout, stderr=sys.stderr)
                p.wait()
            else:
                self.log.critical('storage type [%s] is not supported' % 
                                  self.info['storage'])
                return 1                       
            return p.returncode                       
        except Exception,e:
            self.log.exception(e)
            return 1     
    
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
        
    def read_input_files(self):
        """
        Read and verifies input files passed defines by command line argument(s) 
        
        Overwrites the super method by adding support for optional template files
        """  
        super(WorkflowNodeWrapper, self).read_input_files()
               
        
    
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
    
    