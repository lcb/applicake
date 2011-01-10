#!/bin/env python

'''
Created on Nov 11, 2010

@author: quandtan
'''

import sys,getopt,logging,os,cStringIO
from subprocess import Popen, PIPE
from applicake.utils import Logger as logger

                 
class Application():
    'Application class to prepare and verify the execution of external programs'      
        
    def __call__(self, args):
        "Running the class' main logic and returns the exit code of the validate_run method"      
        self.log.debug('application class file [%s]' % args[0])
        self.log.debug('arguments [%s]' % args[1:])
        self.log.debug('Python class [%s]' % self.__class__.__name__)     
        self.log.info('Start [%s]' % self._validate_args.__name__)
        self._validate_args(args)        
        self.log.info('Finish [%s]' % self._validate_args.__name__)              
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
        self._out_filenames = []
        self._use_filesystem = use_filesystem
        self._log_level = log_level                    
        self._clean_up()
        if use_filesystem:
            self.log = logger(level=self._log_level,file=self._log_filename).logger
        else:
            self.log = logger(level=self._log_level).logger  
            
        #TODO: _validate_args should contain possibility to change log level via commandline argument
                  
    def _clean_up(self):
        'Delete old .out, .err, .log files before initializing the logger'
        files = [self._log_filename,self._stdout_filename,self._stderr_filename]
        for file in files:
            if os.path.exists(file):
                os.remove(file) 
                    
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

    def _validate_args(self,args=None):
        '''
        Validate the command line arguments possibly passed to the application.
        '''
        raise NotImplementedError("Called '_validate_args' method on abstact class")

    def _validate_run(self,run_code=None):
        '''
        Validate the results of the _run() and return [0] if proper succeeded.
        The optional parameter run_code can be passed e.g. when the _run() executed an external application.
        '''
        raise NotImplementedError("Called '_validate_run' method on abstact class")


class ExternalApplication(Application):
    
    def _run(self,command=None):
        'Run and monitor the external application. Returns 1 or the original return code of that application'         
        # when the command does not exist, process just dies.therefore a try/catch is needed
        try:     
            if self._use_filesystem:
                self.stdout = open(self._stdout_filename, 'w+')
                self.stderr = open(self._stderr_filename, 'w+')                           
                p = Popen(command, shell=False, stdout=self.stdout, stderr=self.stderr)
                p.wait()
                #set pointer back to 1st character. therefore, fh has not to be closed (and opened again in validate_run ()
                self.stdout.seek(0)
                self.stderr.seek(0)                                
                return p.returncode                       
            else:
                p = Popen(command, shell=False, stdout=PIPE, stderr=PIPE)            
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


class SimpleApplication(ExternalApplication): 
    'simple application class that takes a string as argument and execute it.'      
    
    def _preprocessing(self):
        return self._command
    
    def _validate_args(self,args):
#        self._command= args[1:]    
        cp = CliParserApplication(description='A simple application to call external programs')  
        parsed_args = cp.get_parsed_args(args[1:])
        if parsed_args['prefix'] is None:
            self.log.fatal('cli argument [prefix] was not set')
            cp.print_usage()
        else:
            self._command = parsed_args['prefix']
        
    def _validate_run(self,run_code):
        print("=== stdout ===")
        print(self.stdout.read())
        print("=== stderr ===")  
        print(self.stderr.read())   
        return run_code
    
                
class SpectraIdentificationApplication(ExternalApplication):
    
    def _preprocessing(self):
        raise NotImplementedError("Called configure method on abstract class") 
        
#    def _validate_args(self,args):                     
#        msg_usage = "USAGE    :" + sys.argv[0] + " --prefix='my.exe' --config=app.conf --template=app.tpl"        
#        try:
#            options, remainder = getopt.getopt(sys.argv[1:], "p:c:t:", ["prefix=", "config=", "template="])
#        except getopt.GetoptError as err:
#            print(msg_usage)
#            self.log.fatal('ERROR PARSING SYS.ARGV [%s]' % self._log_filename)
#            sys.exit(1)
#        if len(options) != 3:  # check if unknown arguments are passed and if all arguments are defined 
#            self.log.fatal("wrong number of arguments [%s]. (Arguments properly not correctly called).\n%s" %(len(options),msg_usage))
#            sys.exit(1)             
#        if len(remainder) > 0:   
#            self.log.fatal("unknown argument")
#            sys.exit(1)             
#        for opt, arg in options:       
#            if opt in ('-p', '--prefix'):                
#                self._command_prefix = arg                  
#            elif opt in ('-c', '--config'):                
#                if not (os.path.exists(arg)):                    
#                    self.log.fatal("File [%s] does not exist.\n%s" % (arg,msg_usage))
#                    sys.exit(1)
#                self._config_filename = arg                  
#            elif opt in ('-t', '--template'):   
#                if not (os.path.exists(arg)): 
#                    self.log.fatal("File [%s] does not exist.\n%s" % (arg,msg_usage))
#                    sys.exit(1) 
#                self._template_filename = arg


    def _validate_args(self,args):     
        cp = CliParserApplication('An application used in MS/MS spectrum analysis')  
        parsed_args = cp.get_parsed_args(args)
        if parsed_args['prefix'] is None:
            self.log.fatal('cli argument [prefix] was not set')
            cp.print_usage()
        else:
            self._command_prefix = parsed_args['prefix']
        if parsed_args['config_filename'] is None:
            self.log.fatal('cli argument [config] was not set')
            cp.print_usage()
        else:
            self._config_filename = parsed_args['config_filename']
            if not os.path.exists(self._config_filename):
                self.log.fatal('file [%s] does not exist' % self._config_filename)
        if parsed_args['tpl_filename'] is None:
            self.log.fatal('cli argument [template] was not set')
            cp.print_usage()
        else:
            self._template_filename = parsed_args['template_filename']
            if not os.path.exists(self._template_filename):
                self.log.fatal('file [%s] does not exist' % self._template_filename)
                
    def create_workdir(self,config):
        basedir = None  
        try:
            basedir = config['DIR'] 
            param_idx = config['PARAM_IDX']
            spectra_idx =  config['SPECTRA_IDX']
            wd = os.path.join(basedir,param_idx)
            wd = os.path.join(wd,spectra_idx)
            wd = os.path.join(wd,self.name)                       
#            wd = os.path.join(basedir,self.name)

#        except:
#            basedir = os.path.abspath(os.curdir)
#            self.log.error('config does not contain a key/value pair for [DIR]: use current dir [%s]' % basedir)
#        basedir = os.path.join(basedir,self.name) 
#        try:
            os.makedirs(wd)
            self.log.debug('Created workdir [%s]' % wd)
        except Exception,e:
            self.log.exception(e)  
            sys.exit(1)
        return wd
    

import argparse,os
class CliParser():
    
    def __init__(self,description=''):
        self.parser = argparse.ArgumentParser(description=description)
        
    
    def get_parsed_args(self,args):
        '''
        parse command line arguments (sys.argv[1:]) and returns a dictionary with the according key value pairs
        '''
        raise NotImplementedError("Called '_preprocessing' method on abstract class") 
    
    def print_usage(self):
        self.parser.parse_args(['-h'])        
    
class CliParserApplication():
    
    def get_parsed_args(self,parser,args):
        self.parser.add_argument('-p', action="store", dest="p",type=str,help="prefix of the command to execute")
        self.parser.add_argument('-c', action="store", dest="c",type=str,help="configuration file in ini file structure")
        self.parser.add_argument('-t', action="store", dest="t",type=str,help="template of the program specific input file")
#        parser.add_argument('-b', action="store_true", dest='2', default=False,help='test of a boolean')
#        parser.add_argument('-i', action="store", dest="3", default=0, type=int,help='test of a integer')
        a = self.parser.parse_args(args)
        return {'prefix':a.p,'config_filename':a.c,'tpl_filename':a.t}
        
            
    
    
    
    



        
