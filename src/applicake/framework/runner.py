#!/bin/env python

'''
Created on Nov 11, 2010

@author: quandtan
'''

import os
import shutil
import sys
from cStringIO import StringIO
from subprocess import Popen
from subprocess import PIPE
from applicake.framework.argshandler import ArgsHandler
from applicake.framework.enums import KeyEnum
from applicake.framework.logger import Logger
from applicake.framework.interfaces import IApplication
from applicake.framework.interfaces import IWrapper
from applicake.framework.informationhandler import BasicInformationHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.fileutils import FileLocker
from applicake.utils.dictutils import DictUtils                          
                 
                 
class Runner(KeyEnum):
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
        default_info = {
                        self.STORAGE:'memory',
                        self.LOG_LEVEL:'DEBUG',
                        self.NAME: app.__class__.__name__,
                        self.CREATED_FILES: []
                        } 
        tmp_log_stream = StringIO()
        exit_code = 1
        try:
            # create memory logger            
            log = Logger.create(level=default_info[self.LOG_LEVEL],name='memory_logger',stream=tmp_log_stream)
            log.debug('created temporary in-memory logger')
            # get command line arguments
            args = sys.argv
            log.debug('application class file [%s]' % args[0])
            log.debug('arguments [%s]' % args[1:])
            log.debug('Runner class [%s]' % self.__class__.__name__)
            log.debug('Application class [%s]' % app.__class__.__name__)
            log.info('Start [%s]' % self.get_args_handler.__name__)
            args_handler = self.get_args_handler()
            log.info('Start [%s]' % app.set_args.__name__)   
            args_handler = app.set_args(log,args_handler)
            log.info('Start [%s]' % args_handler.get_parsed_arguments.__name__)
            try:
                pargs = args_handler.get_parsed_arguments(log)
            except:
                # need to reset streams in order to allow args_handler to print usage message
                self.reset_streams() 
                return exit_code
            log.info('Start [%s]' % self.get_info_handler.__name__)
            info_handler = self.get_info_handler()
            log.info('Start [%s]' % info_handler.get_info.__name__)
            info = info_handler.get_info(log, pargs)
            log.debug('content of info [%s]' % info)
            info = DictUtils.merge(info, default_info,priority='left')
            log.debug('Added default values to info they were not set before')            
            log.debug('content of final info [%s]' % info)    
            log.info('Start [%s]' % self.get_streams.__name__)               
            (self.out_stream,self.err_stream,self.log_stream) = self.get_streams(info,log)                
            sys.stdout = self.out_stream
            log.debug('set sys.out to new out stream')
            sys.stderr = self.err_stream
            log.debug('set sys.err to new err stream')
            log.debug('redirect sys streams for stdout/stderr depending on the chosen storage type')                      
            log = Logger.create(level=info[self.LOG_LEVEL],
                         name=info[self.NAME],stream=self.log_stream)      
            log.debug('created new logger dependent of the storage')
            tmp_log_stream.seek(0)
            self.log_stream.write(tmp_log_stream.read())
            log.debug('wrote content of temporary logger to new logger')                
            log.info('Start [%s]' % self.create_workdir.__name__)
            info = self.create_workdir(info,log) 
            log.info('Start [%s]' % self.run_app.__name__)
            exit_code,info = self.run_app(app,info,log,args_handler)
            if exit_code != 0:
                log.fatal('exit code of run_app() != 0')
                sys.exit(1)              
            log.info('Start [%s]' % info_handler.write_info.__name__)
            info_handler.write_info(info,log)
            log.info('Start [%s]' % self._cleanup.__name__)
            exit_code,info,log = self._cleanup(info,log)
            log.debug('info [%s]' % info)
            log.debug('exit code [%s]' %exit_code)                 
        except Exception, e:
            log.fatal('error in __call__')
            log.exception(e) 
            self.reset_streams() 
        finally:
            log.info('Start [%s]' % self.reset_streams.__name__)
            self.reset_streams()      
            # needed for guse/pgrade
            if hasattr(self, 'log_stream'): 
                stream = self.log_stream
            else:
                stream = tmp_log_stream               
            stream.seek(0)
            sys.stderr.write(stream.read())            
            self.info = info    
            return exit_code
        
    def _cleanup(self,info,log):
        """
        Does the final clean-up
        
        - copies input files and output file to working dir
        - copies created files to working dir
        - If storage='memory' is used, out and err stream are printed to stdout
        - log stream is printed to stderr
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages   
        
        @rtype: (int,dict,logger)
        @return: Tuple of 3 objects; the exit code,the (updated) info object and the updated logger.          
        """         
        log.info('Start [%s]' % self.reset_streams.__name__)
        self.reset_streams()
        log.info('Finished [%s]' % self.reset_streams.__name__)
        log.debug('found key [%s] [%s]' % (self.WORKDIR, info.has_key(self.WORKDIR)))        
        if info.has_key(self.WORKDIR):
            wd = info[self.WORKDIR]
            log.debug('start copying/moving files to work dir')
            # copy input files to working directory
            files_to_copy = []
            if info.has_key(self.INPUT):
                DictUtils.get_flatten_sequence([files_to_copy,info[self.INPUT]])
                log.debug('found following input files to copy [%s]' % info[self.INPUT])
                files_to_copy.extend(info[self.INPUT])
            if info.has_key(self.OUTPUT):
                DictUtils.get_flatten_sequence([files_to_copy,info[self.OUTPUT]])
                log.debug('found following output file to copy [%s]' % info[self.OUTPUT])
                files_to_copy.append(info[self.OUTPUT])            
            for path in files_to_copy:
                # 'r' escapes special characters
                src = r'%s' % os.path.abspath(path) 
                try:
                    shutil.copy(src,wd) 
                    log.debug('Copied [%s] to [%s]' % (src,wd))
                except:
                    log.critical('Counld not copy [%s] to [%s]' % (src,wd))
                    return (1,info,log)            
        if info[self.STORAGE] == 'memory':
            print '=== stdout ==='
            self.out_stream.seek(0)
            for line in self.out_stream.readlines():
                print line
            print '=== stderr ==='
            self.err_stream.seek(0)
            for line in self.err_stream.readlines():
                print line                              
        # move created files to working directory
        # 'created_files might be none e.g. if memory-storage is used   
        if info[self.CREATED_FILES] != []:  
            for path in info[self.CREATED_FILES]:
                # check if element is a key of info and not an actual file
                if info.has_key(path):
                    path = info[path]
                    src = r'%s' % os.path.abspath(path) 
                    dest = r'%s' % os.path.join(wd,os.path.basename(path))
                    info[path] = dest
                    log.debug('set value of key [%s] from [%s] to [%s]' % (path,info[path],dest))
                else:
                    src = r'%s' % os.path.abspath(path) 
                    dest = r'%s' % os.path.join(wd,os.path.basename(path))                    
                try:
                    shutil.copy(src,wd)
                    log.debug('Copy [%s] to [%s]' % (src,dest))
                except:
                    log.fatal('Stop program because could not copy [%s] to [%s]' % (src,dest))
                    return(1,info,log)
        return (0,info,log)   
    
    def _get_app_specific_info(self,info,args_handler):
        """
        Return a subset of info that depends on the application-specific arguments
        """ 
        return {k: info[k] for k in args_handler.get_app_argnames()}

                                                
                    
    def _set_jobid(self,info,log):
        """
        Uses a file-based system to retrieve a job id.
        
        Creates a file in a base dir that holds the last job id and increases it incrementally.
        If the 'jobid.txt' does not exists, it is initiated with the job id '1'.
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages  
        """
        jobid = 0
        if not info.has_key(self.BASEDIR):
            log.info("info has not key [%s]." % self.BASEDIR)
        else:    
            dirname = info[self.BASEDIR]
            log.debug('found base dir [%s]' % dirname)
            filename = os.path.join(dirname, 'jobid.txt')
            locker = FileLocker()
            if (os.path.exists(filename)):            
                fh = open(filename,'r') 
                locker.lock(fh,locker.LOCK_EX) 
                jobid= int(fh.read())   
                log.debug('previous job id [%s]' % jobid)
                jobid += 1         
                log.debug('current job id [%s]' % jobid)
            fh = open(filename,'w')    
            fh.write(str(jobid))
            locker.unlock(fh)            
        info[self.JOB_IDX]=jobid    
        log.debug("added key [%s] to info object" % self.JOB_IDX)
        
    def create_workdir(self,info,log):
        """
        Create a working directory.
        
        The location is stored in the info object with the key [%s].
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages  
        
        @rtype info: dict         
        @return info: Dictionary object with the (updated) information needed by the class        
        """ % self.WORKDIR
        
        keys = [self.BASEDIR,self.JOB_IDX,self.PARAM_IDX,self.FILE_IDX,self.NAME]
        if not info.has_key(keys[0]):
            log.info('info object does not contain key [%s], use current dir [%s] instead' % (keys[0],os.getcwd()))      
        if not info.has_key(keys[1]):
            self._set_jobid(info,log)               
        path_items = []    
        for k in keys:
            if info.has_key(k):
                path_items.append(info[k])
        # join need a list of strings.
        # the list has to be parsed explicitly because list might contain integers       
        path = (os.path.sep).join(map( str, path_items ) ) 
        # creates the directory, if it exists, it's content is removed       
        FileUtils.makedirs_safe(log,path,clean=True)
        info[self.WORKDIR] = path  
        log.debug("added key [%s] to info object." % self.WORKDIR)    
        return info                     
                    
    def get_streams(self,info,log):
        """
        Initializes the streams for stdout/stderr/log.
        
        The type of the streams depends on the 'info' object.
        
        @precondition: 'info' object that has to contain the keys [%s,%s]
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages  
        
        Return: Tuple of boolean, message that explains boolean,
        out_stream, err_stream, log_stream        
        """ % (self.STORAGE,self.NAME)      
        required_keys = [self.STORAGE,self.NAME]
        for key in required_keys:
            log.debug('found key [%s]: [%s]' % (key, info.has_key(key)))
        storage = info[self.STORAGE]
        log.debug('STORAGE type: [%s]' % storage)
        if storage == 'memory':
            out_stream = StringIO()            
            err_stream = StringIO() 
            log_stream = StringIO() 
            log.debug('Created in-memory streams')                                      
        elif storage == 'file':
            out_file = ''.join([info[self.NAME],".out"])
            err_file = ''.join([info[self.NAME],".err"]) 
            log_file = ''.join([info[self.NAME],".log"])                      
            created_files = [out_file,err_file,log_file]
            info[self.CREATED_FILES] = created_files
            log.debug("add [%s] to info['CREATED_FILES'] to copy them later to the work directory" % created_files)            
            # streams are initialized with 'w+' that files newly created and therefore previous versions are deleted.
            out_stream = open(out_file, 'w+',buffering=0)            
            err_stream = open(err_file, 'w+',buffering=0)  
            log_stream = open(log_file,'w+',buffering=0)
            log.debug('Created file-based streams')                                 
        else:                        
            log.fatal('Exit program because storage type is not supported.')
            sys.exit(1)
        return (out_stream,err_stream,log_stream)  
    
    
    def reset_streams(self):
        """
        Reset the stdout/stderr to their default
        """
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__                  
    
    def get_args_handler(self):
        """
        Define which command line argument handler to use
        
        @rtype: IArgsHandler
        @return: An implementation of the IArgsHandler interface. 
        """ 
        raise NotImplementedError("get_args_handler() is not implemented.")
    
    def get_info_handler(self):
        """
        Define which information handler to use
        
        @rtype: IInformation
        @return: An implementation of the IInformation interface. 
        """     
        raise NotImplementedError("get_info_handler() is not implemented.")
    
    def run_app(self,info,log,app):
        """
        Executes an object that implements the supported Application interface.        
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages  
        @type app: 
        @param app: Object that implements a supported interface from the interface module  
        
        @rtype: (int,dict)
        @return: Tuple of 2 objects; the exit code and the (updated) info object.
        """
        raise NotImplementedError("run() is not implemented.")                                                                                                                                           
                                                                        

class ApplicationRunner(Runner):
    """    
    Runner class that supports application that implement the IApplication interface.
    """
    
    def get_args_handler(self):
        """
        See super class
        """
        return ArgsHandler()

    def get_info_handler(self):  
        """
        Information from the command line and the input file(s) are merged with priority to the
        command line information.
        Output is only written to a single file
        """       
        return BasicInformationHandler()                  
    
    def run_app(self,app,info,log,args_handler):
        """
        Run a python application
        
        See super class.
        """  
        exit_code = None     
        if isinstance(app,IApplication):
            log.info('Start [%s]' % self._get_app_specific_info.__name__)
            app_info = self._get_app_specific_info(info, args_handler)
            log.debug('app_info [%s]' % app_info)
            log.info('Finished [%s]' % self._get_app_specific_info.__name__)
            exit_code,app_info = app.main(app_info,log)   
            log.debug('content of app_info after running app [%s]' % app_info)    
            info = DictUtils.merge(info, app_info,priority='left')    
            log.debug('content of info after merge with app_info [%s]' % info)
        else:                                    
            self.log.critical('the object [%s] is not an instance of one of the following %s'% 
                              (app.__class__.__name__,
                               [IApplication,__class__.__name__]))  
            exit_code = 1
        return exit_code,info
    

class GeneratorRunner(ApplicationRunner):
    """
    Specific runner for generator applications.
    """

    def run_app(self,app,info,log,args_handler):
        """
        Specific runner for the generators.
        
        Generators require access to the complete info object, not only to specific informations.
        See super class.
        """  
        exit_code = None     
        if isinstance(app,IApplication):
            exit_code,info = app.main(info,log)   
        else:                                    
            self.log.critical('the object [%s] is not an instance of one of the following %s'% 
                              (app.__class__.__name__,
                               [IApplication,__class__.__name__]))  
            exit_code = 1
        return exit_code,info           
        

class WrapperRunner(ApplicationRunner):
    """
    Runner class that supports application that implement the IWrapper interface      
        
    The Application type is used to create workflow nodes that 
    prepare, run and validate the execution of an external application.
    """
    
    def _run(self,command,storage):
        """
        Execute a command and collects it's output in self.out_stream and self.err_stream.
         
        The stdout and stderr are written to files if file system should be used.
        Otherwise stdout and stderr of the application are separately printed to 
        stdout because the logger uses by default the stderr.
        
        @type command: string
        @param command: Command that will be executed
        @type storage: string
        @param storage: Storage type for the out/err streams produced by the command line execution  
        
        @rtype: int
        @return: Return code. It is either 1 or the original return code of the executed command.        
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
                                  self.info[self.STORAGE])
                return 1                       
            return p.returncode                       
        except Exception,e:
            self.log.exception(e)
            return 1                          
    
    def run_app(self,app,info,log,args_handler):
        """
        Prepare, run and validate the execution of an external program. 
        
        See super class.
        """
        exit_code = None
        if isinstance(app,IWrapper):
            
            log.info('Start [%s]' % self._get_app_specific_info.__name__)
            app_info = self._get_app_specific_info(info, args_handler)
            log.debug('app_info [%s]' % app_info)
            log.info('Finished [%s]' % self._get_app_specific_info.__name__)
            log.info('Start [%s]' % app.prepare_run.__name__)
            command,app_info = app.prepare_run(app_info,log)                 
            log.info('Finish [%s]' % app.prepare_run.__name__)
            log.debug('content of app_info [%s]' % app_info)    
            info = DictUtils.merge(info, app_info,priority='left')    
            log.debug('content of info after merge with app_info [%s]' % info)             
            if command is None:
                log.critical('Command was [None]. Interface of [%s] is possibly not correctly implemented' %
                                  app.__class__.__name__)
                exit_code = 1
            else:    
                # necessary when e.g. the template file contains '\n' what will cause problems 
                # when using concatenated shell commands
                log.debug('remove all [\\n] from command string')
                command  = command.replace('\n','')   
                log.info('Command [%s]' % str(command))             
                log.info('Start [%s]' % self._run.__name__)
                run_code = self._run(command,info[self.STORAGE])
                log.info('Finish [%s]' % self._run.__name__)
                log.info('run_code [%s]' % run_code)        
                log.info('Start [%s]' % app.validate_run.__name__)
                # set stream pointer the start that in validate can use 
                # them immediately with .read() to get content
                self.out_stream.seek(0)
                self.err_stream.seek(0)
                log.info('Start [%s]' % self._get_app_specific_info.__name__)
                app_info = self._get_app_specific_info(info, args_handler)
                log.debug('app_info [%s]' % app_info)
                log.info('Finished [%s]' % self._get_app_specific_info.__name__)                
                exit_code,app_info = app.validate_run(app_info,log,run_code,self.out_stream,self.err_stream)
                log.debug('exit code [%s]' % exit_code)
                log.debug('content of app_info [%s]' % app_info)                        
                log.info('Finish [%s]' % app.validate_run.__name__) 
                info = DictUtils.merge(info, app_info,priority='left')    
                log.debug('content of info after merge with app_info [%s]' % info) 
        else:                                   
            log.critical("the object [%s] is not an instance of one of the following [%s]" % (app.__class__.__name__ ,
                                                                                                 IWrapper.__class__.__name__))  
            exit_code = 1
        return exit_code,info