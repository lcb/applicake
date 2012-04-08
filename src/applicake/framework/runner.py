#!/bin/env python

'''
Created on Nov 11, 2010

@author: quandtan
'''

import os
import shutil
import sys
from argparse import ArgumentParser
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.logger import Logger
from applicake.framework.confighandler import ConfigHandler
from applicake.framework.interfaces import IApplication
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.fileutils import FileLocker
from applicake.utils.dictutils import DictUtils                
                 
class ApplicationInformation(dict):
    """
    Information about the application object.
    """     
                 
class Runner(object):
    """
    Basic class to prepare and run one of the Interface classes of the framework as workflow node    
    """    
    
    def __call__(self, args,app):
        """
        Program logic of the Application class.
        First, the command line arguments are parsed and validated. 
        Then, the main program logic is executed.
        
        Return: exit code (integer)
        """      
        try:
            log_msg = []
            # create Application information object and add information        
            info = ApplicationInformation()            
            # set name variable to concrete class name if no specific name is provided.
            # the name variable is used to for the logger and file names if the file system is used                      
            log_msg.append('Start [%s]' % self.get_parsed_arguments.__name__)
            pargs = self.get_parsed_arguments()
            log_msg.append('Finish [%s]' % self.get_parsed_arguments.__name__)
            info.update(pargs)
            log_msg.append('Update application information with settings from command line') 
            created_files = {'CREATED_FILES':None}
            info.update(created_files)
            log_msg.append("Add/reset key [CREATED_FILES] to application information")                                   
            config = {}
            for fin in pargs['INPUTS']:          
                valid, msg = FileUtils.is_valid_file(self,fin)
                if not valid:
                    log_msg.append(msg + '')
                    sys.stderr.write(log_msg)
                    sys.exit(1)
                else:
                    log_msg.append('file [%s] is valid' % fin)
                    new_config = ConfigHandler().read(fin)
                    log_msg.append('created dictionary from file content')
                    config = DictUtils.merge(self,config, new_config,priority='flatten_sequence') 
                    log_msg.append('merge content with content from previous files')
            # merge the content of the input files with the already existing 
            # priority is on the first dictionary
            info = DictUtils.merge(self, info, config,priority='left') 
            # set default for name if non is given via the cmdline or the input file
            info = DictUtils.merge(self, info, {'NAME': app.__class__.__name__})
            (success,msg,
             self.out_stream,
             self.err_stream,
             self.log_stream) = self._get_streams(info)
            if not success:
                log_msg.append(msg)
                sys.exit(1)
            else:
                log_msg.append(msg)
                # redirect default stdout/stderr to stream objects    
                sys.stdout = self.out_stream
                sys.stderr = self.err_stream
                # create logger
                self.log = Logger(level=info['LOG_LEVEL'],
                                  name=info['NAME'],stream=self.log_stream).logger  
        
        
#            self._init_streams(info['STORAGE'],info['NAME'],info['LOG_LEVEL'])        
            log_msg.append('init streams')
            for msg in log_msg:
                self.log.debug(msg)
            self.log.debug('application class file [%s]' % args[0])
            self.log.debug('arguments [%s]' % args[1:])
            self.log.debug('Python class [%s]' % self.__class__.__name__)  
            self.log.info('Start [%s]' % self._set_wd.__name__)
            self._set_wd(info,self.log)
            self.log.info('Finished [%s]' % self._set_wd.__name__)                                  
            self.log.info('Start [%s]' % self.run_app.__name__)
            exit_code = self.run_app(app,info)
            self.log.info('Finished [%s]' % self.run_app.__name__)               
            self.log.info('Start [%s]' % self.write_output_file.__name__)
            self.write_output_file(info,info['OUTPUT'])
            self.log.info('Finished [%s]' % self.write_output_file.__name__)
            self.log.info('Start [%s]' % self._cleanup.__name__)
            self._cleanup(info,self.log)
            self.log.info('Finished [%s]' % self._cleanup.__name__)            
            self.info = info       
            self.log.info('exit_code [%s]' % exit_code)
            return int(exit_code)
        except:
            self._reset_standard_streams()
            for msg in log_msg:
                sys.stderr.write("%s\n" % msg)

            raise   
    
    def _cleanup(self,info,log):
        """
        Does the final clean-up
        
        - copies input files and output file to working dir
        - moves created files to working dir
        - If storage='memory' is used, out and err stream are printed to stdout
        and log stream is printed to stderr
        
        Arguments:
        - info: Configuration object to access file and parameter information 
        - log: Logger to store log messages               
        """ 
        wd = info['WORKDIR']
        log.debug('start copying/moving files to work dir')
        # copy input files to working directory
        
        files_to_copy = DictUtils.get_flatten_sequence([info['INPUTS'],info["OUTPUT"]])  
        for path in files_to_copy:
            # 'r' escapes special characters
            src = r'%s' % os.path.abspath(path) 
            try:
                shutil.copy(src,wd) 
                log.debug('Copied [%s] to [%s]' % (src,wd))
            except:
                log.critical('Counld not copy [%s] to [%s]' % (src,wd))
                sys.exit(1)             
        self._reset_standard_streams()  
        if info['STORAGE'] == 'memory':
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
        # move created files to working directory
        # 'created_files might be none e.g. if memory-storage is used   
        if info['CREATED_FILES'] is not None:  
            for path in info['CREATED_FILES']:
                src = r'%s' % os.path.abspath(path) 
                dest = r'%s' % os.path.join(wd,os.path.basename(path))
                try:
                    shutil.move(src,wd)
                    print('Move [%s] to [%s]' % (src,dest))
                except:
                    sys.stderr.write('Could not move [%s] to [%s]' % (src,dest))
                    sys.exit(1) 
                    
    def _get_jobid(self,dirname):
        """
        Uses a file-based system to retrieve a job id.
        
        Creates a file in a base dir that holds the last job id and increases it incrementally.
        If the 'jobid.txt' does not exists, it is initiated with the job id '1'.
        
        Arguments:
        - dirname: Path of the base directory.
        
        Return: the job id 
        """
        jobid = 1
        filename = os.path.join(dirname, 'jobid.txt')
        locker = FileLocker()
        if (os.path.exists(filename)):            
            fh = open(filename,'r') 
            locker.lock(fh,locker.LOCK_EX) 
            jobid= int(fh.read())   
            jobid += 1         
        fh = open(filename,'w')    
        fh.write(str(jobid))
        locker.unlock(fh)            
        return jobid                                                 
                
    def _get_streams(self,info):
        """
        Initializes the streams for stdout/stderr/log
        
        Arguments:
        - storage: defines where to store the streams
        -- memory: in-memory
        -- file: file-based
        - name: name used for file-based storage
        
        Return: Tuple of boolean, message that explains boolean,
        out_stream, err_stream, log_stream        
        """   
        success = True
        msg = ''  
        if info['STORAGE'] == 'memory':
            out_stream = StringIO()            
            err_stream = StringIO() 
            log_stream = StringIO() 
            msg = 'Created in-memory streams'                                      
        elif info['STORAGE'] == 'file':
            out_file = ''.join([info['NAME'],".out"])
            err_file = ''.join([info['NAME'],".err"]) 
            log_file = ''.join([info['NAME'],".log"])
            # add files to info object to copy them later to the work directory            
            info['CREATED_FILES'] = [out_file,err_file,log_file]
            # streams are initialized with 'w+' that files are pured first before
            # writing into them         
            out_stream = open(out_file, 'w+')            
            err_stream = open(err_file, 'w+')  
            log_stream = open(log_file,'w+')
            
            msg = 'Created file-based streams'                                 
        else:
            success = False
            msg = 'No streams created because type [%s] is not supported' % info['STORAGE']
        return (success,msg,out_stream,err_stream,log_stream)  
    
    
    def _reset_standard_streams(self):
        """
        Reset the stdout/stderr to their default
        """
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__           
         
    def _set_wd(self,info,log):
        keys = ['BASEDIR','JOB_IDX','PARAM_IDX','FILE_IDX','NAME']
        if not info.has_key(keys[0]):
            log.critical('info object does not contain key [%s]' % keys[0])
            log.critical('content of info [%s]' % info)
            sys.exit(1)
        if not info.has_key(keys[1]):
            info['JOB_IDX'] = self._get_jobid(info['BASEDIR'])                
        path_items = []    
        for k in keys:
            if info.has_key(k):
                path_items.append(info[k])
        # join need a list of strings.
        # the list has to be parsed explicitly because list might contain integers       
        path = (os.path.sep).join(map( str, path_items ) )  
        # creates the directory, if it exists, it's content is removed       
        success, msg = FileUtils.makedirs_safe(path,clean=True)
        if success:
            log.debug(msg)
        else:
            log.critical(msg)
            sys.exit(1)        
        info['WORKDIR'] = path                 
             
    def define_arguments(self, parser):        
        """
        Define command line arguments of the application.
        
        Arguments:
        - parser: Object of type ArgumentParser
        """        
        raise NotImplementedError("define_arguments() is not implemented.")   
    
    def get_parsed_arguments(self):
        """
        Parse command line arguments of the application.
        
        Return: Dictionary of parsed arguments        
        """
        raise NotImplementedError("get_parsed_arguments() is not implemented.") 

    def run_app(self,app,info):
        """
        Runs one of the supported interface classes.
        
        Arguments:
        - app: Object that inherited one of the supported interfaces
        
        Return: Exit code (0 for successful check). 
        """
        raise NotImplementedError("run() is not implemented.") 
                                                                        
    
    def write_output_file(self,info,filename): 
        self.log.debug('output file [%s]' % filename)                  
        ConfigHandler().write(info, filename) 
        valid,msg = FileUtils.is_valid_file(self, filename)
        if not valid:
            self.log.fatal(msg)
            sys.exit(1)
            


class ApplicationRunner(Runner):
    """
    Used to run a class that implements the Application interface

    Return: exit code (integer)    
    """
    
    def define_arguments(self, parser):
        """
        See super class.
        """
        # argument input file: is requred and returns a list if defined multiple times
        parser.add_argument('-i','--input',required=True,dest="INPUTS", 
                            action='append',help="Input (configuration) file(s)")
        # argument output file: is requred and returns a list if defined multiple times
        parser.add_argument('-o','--output',required=False, dest="OUTPUT",
                            action='store',help="Output (configuration) file")
        parser.add_argument('-n','--name',required=False, dest="NAME", 
#                            default=self.__class__.__name__,
                            help="Name of the workflow node")
        parser.add_argument('-s','--storage',required=False, dest="STORAGE", 
#                            default=None,
                            choices=['memory','file'],
                            help="Storage type for produced streams")  
        parser.add_argument('-l','--loglevel',required=False, dest="LOG_LEVEL", 
#                            default=None,
                            choices=['DEBUG','INFO','WARNING',
                                                  'ERROR','CRITICAL'],
                            help="Storage type for produced streams")        

    def get_parsed_arguments(self):
        """
        See super class.
        """        
        parser = ArgumentParser(description='Applicake application')
        self.define_arguments(parser=parser) 
        args = vars(parser.parse_args(sys.argv[1:]))
        # if optional args are not set, a key = None is created
        # these have to be removed
        args =DictUtils.remove_none_entries(args)
        return args
    
    def run_app(self,app,info):
        """
        Run a Python program
        
        Arguments:
        - app: Implementation of the IApplication interface
        
        Return: Exit code (integer) 
        """        
        if isinstance(app,IApplication):
            return app.main(info,self.log)
        else:                                    
            self.log.critical('the object [%s] is not an instance of one of the following %s'% 
                              (app.__class__.__name__,
                               [IApplication,__class__.__name__]))  
            return 1
    


class WrapperRunner(ApplicationRunner):
    """
    The Application type is used to create workflow nodes that 
    prepare, run and validate the execution of an external application.
    
    Return: Exit code (integer) 
    """
    
    def _run(self,command,storage):
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
            if storage == 'memory':
                p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)            
                output, error = p.communicate()                                                                                                                                                                            
                self.out_stream = StringIO(output)
                self.err_stream = StringIO(error)  
            elif storage == 'file':
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
        super(WrapperRunner, self).define_arguments(parser=parser)
        parser.add_argument('-p','--prefix',required=False, dest="prefix",
                            help="Prefix of the command to execute")      
        parser.add_argument('-t','--template',required=False, dest="template", 
                            help="Name of the workflow node")               
    
    def run_app(self,app,info):
        """
        Prepare, run and validate the execution of an external program.
        
        Arguments:
        - app: Implementation of the IWrapper interface
        
        Return: Exit code (integer) 
        """
        if isinstance(app,IWrapper):
            self.log.info('Start [%s]' % app.prepare_run.__name__)
            command = app.prepare_run(info,self.log)     
            self.log.info('Finish [%s]' % app.prepare_run.__name__)
            if command is None:
                self.log.critical('Command was [None]. Interface of [%s] is possibly not correctly implemented' %
                                  app.__class__.__name__)
                return 1                
            # necessary when e.g. the template file contains '\n' what will cause problems 
            # when using concatenated shell commands
            self.log.debug('remove all [\\n] from command string')
            command  = command.replace('\n','')   
            self.log.info('Command [%s]' % str(command))
            self.log.info('Start [%s]' % self._run.__name__)
            run_code = self._run(command,info['STORAGE'])
            self.log.info('Finish [%s]' % self._run.__name__)
            self.log.info('run_code [%s]' % run_code)        
            self.log.info('Start [%s]' % app.validate_run.__name__)
            # set stream pointer the start that in validate can use 
            # them immediately with .read() to get content
            self.out_stream.seek(0)
            self.err_stream.seek(0)
            exit_code = app.validate_run(info,self.log,run_code,self.out_stream,self.err_stream)
            self.log.debug('exit code [%s]' % exit_code)
            self.log.info('Finish [%s]' % app.validate_run.__name__)        
            return exit_code
        else:                                    
            self.log.critical('the object [%s] is not an instance of one of the following %s'% 
                              (app.__class__.__name__,
                               [IApplication,__class__.__name__]))  
            return 1        
    
    