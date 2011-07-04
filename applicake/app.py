#!/bin/env python

'''
Created on Nov 11, 2010

@author: quandtan
'''

import sys,getopt,logging,os,cStringIO,argparse,glob,shutil
from subprocess import Popen, PIPE
from applicake.utils import Logger as logger
from applicake.utils import IniFile,Workflow,Utilities
                 
class Application(object):
    'Application class to prepare and verify the execution of external programs'      
        
    def __call__(self, args):
        "Running the class' main logic and returns the exit code of the validate_run method"      
        self.log.debug('application class file [%s]' % args[0])
        self.log.debug('arguments [%s]' % args[1:])
        self.log.debug('Python class [%s]' % self.__class__.__name__)   
        self.log.info('Start [%s]' % self._get_parsed_args.__name__)
        parsed_args = self._get_parsed_args(args[1:])        
        self.log.info('Finish [%s]' % self._get_parsed_args.__name__)          
        self.log.info('Start [%s]' % self._validate_parsed_args.__name__)
        self._validate_parsed_args(parsed_args)        
        self.log.info('Finish [%s]' % self._validate_parsed_args.__name__)              
        self.log.info('Start [%s]' % self._preprocessing.__name__)
        command = self._preprocessing()     
        self.log.info('Finish [%s]' % self._preprocessing.__name__)
        if command is not None:
            #necessary when e.g. the template file contains '\n' what will cause problems when using concatenated shell commands
            self.log.debug('remove all [\\n] from command string')
            command  = command.replace('\n','')   
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
        return int(exit_code)
    
    def __init__(self, use_filesystem=True,log_level=logging.DEBUG,name=None,log_console=True):
        'Initialization of variables and basic preparation of running the class'
        if name is None:
            name = str(self.__class__.__name__).lower()
        self.name=name.lower()  
        self._stdout_filename = ''.join([self.name,".out"])
        self._stderr_filename = ''.join([self.name,".err"]) 
        self._log_filename = ''.join([self.name,".log"])
        self._params_ext = ".params"
        self._tpl_ext = ".tpl"
        self._result_ext = ".result"
        self._use_filesystem = use_filesystem
        self._log_level = log_level                    
        self._clean_up()
        if use_filesystem:
            self.log = logger(level=self._log_level,name=self.name,file=self._log_filename,console=log_console).logger
        else:
            self.log = logger(level=self._log_level,console=log_console).logger  
        self.log.debug(os.path.abspath(self._log_filename))    
        #TODO: _validate_parsed_args should contain possibility to change log level via commandline argument
                  
    def _clean_up(self):
        'Delete old .out, .err, .log files before initializing the logger'
        files = [self._log_filename,self._stdout_filename,self._stderr_filename]
        for file in files:
            if os.path.exists(file):
                os.remove(file) 
                
    def _get_parsed_args(self,args):        
        '''
        Parse command line arguments and returns dictionary with according key/value pairs
        '''
        # need to pass args as otherwise sys.argv is used and this complicates this for the collector
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
    
    def _get_parsed_args(self,args):
        parser = argparse.ArgumentParser(description='A simple application to call external programs')
        parser.add_argument('-p','--prefix', action="store", dest="p",type=str,help="prefix of the command to execute")
        a = parser.parse_args(args)
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
    
    def _get_app_inputfilename(self,config):
        return None
    
    def _get_command(self,prefix,input_filename):
        raise NotImplementedError("Called '_get_command' method on abstact class")     
    
    def _get_parsed_args(self,args):
        parser = argparse.ArgumentParser(description='Wrapper around a spectra identification application')
        parser.add_argument('-p','--prefix',required=True, nargs=1,action="store", dest="prefix",type=str,help="prefix of the command to execute")
        parser.add_argument('-i','--input',required=True, nargs=1,action="store", dest="input_filename",type=str,help="input file")
        parser.add_argument('-o','--output',required=True,nargs=1, action="store", dest="output_filename",type=str,help="output file")
        parser.add_argument('-n','--name',required=False,default=self.name,nargs=1, action="store", dest="name",type=str,help="identifier used in the process")
        a = parser.parse_args(args)
        if type(a.name) is list:
            a.name = a.name[0]        
        return {'prefix':a.prefix[0],'input_filename':a.input_filename[0],'output_filename':a.output_filename[0],'name':a.name}      
    
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
        self.log.info('Start %s' % self._get_command.__name__)
        command = self._get_command(prefix=self._command_prefix,input_filename=app_input_filename)   
        self.log.info('FINISHED %s' % self._get_command.__name__)
        return command   
    
    def _validate_parsed_args(self,dict):   
        self._command_prefix = dict['prefix']
        self._input_filename = dict['input_filename']
        self.log.debug("input file [%s]" % os.path.abspath(self._input_filename))
        if not os.path.exists(self._input_filename):
            self.log.fatal('file [%s] does not exist' % self._input_filename)
            sys.exit(1)
        self._output_filename = dict['output_filename']                                  
        self.name = dict['name']
                
    def create_workdir(self,config):
        wd = None
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
            if os.access( wd, os.F_OK):
                self.log.warning("dir [%s] already exists and can be accessed" % wd)
                self.log.debug('delete old dir')
                shutil.rmtree(wd)
                self.log.debug('create dir')
                os.makedirs(wd)
            else:                
                self.log.warning(e)  
                sys.exit(1)
        return wd    
    
    def _validate_run(self,run_code):
        output = os.path.abspath(self._output_filename)
        result = os.path.abspath(self._result_filename)        
        if 0 < run_code:
            return run_code 
        if not os.path.exists(result):
            self.log.error('File [%s] does not exist' % result)
            return 1
        else:
            self.log.debug('File [%s] does exist' % result)
        if not os.path.exists(output):
            self.log.error("File [%s] does not exist" % output)
            return 1
        else:
            self.log.debug("File [%s] does exist" % output)
            self.log.debug("content:%s" % self._iniFile.read_ini())               
        for line in self.stderr.readlines():
            if 'command not found' in line:
                self.log.error(line)
                return 1  
        filesize = os.path.getsize(self._result_filename)
        self.log.debug('file size [%s] of result file [%s] is > 0 KB' % (filesize,self._result_filename))
        if 0 == filesize:
            self.log.error('file size is too small')
            return 1  
        ## TODO: check on stderr that 'command not found' does not appear
        return 0                                                   
                            
class TemplateApplication(WorkflowApplication):     
    
    def _get_app_inputfilename(self,config):
        dest = os.path.join(self._wd,self.name + self._params_ext)
        Utilities().substitute_template(template_filename=self._template_filename,dictionary=config,output_filename=dest)
        return dest   
    
#    def _preprocessing(self):
#        self.log.debug('Read input file [%s]' % os.path.abspath(self._input_filename))
#        self._iniFile = IniFile(input_filename=self._input_filename,output_filename=self._output_filename)
#        config = self._iniFile.read_ini()                
#        self.log.debug("content: %s" % config)
#        self.log.info('Start %s' % self.create_workdir.__name__)
#        self._wd = self.create_workdir(config)
#        self.log.info('Finished %s' % self.create_workdir.__name__) 
#        self.log.info('Start %s' % self._get_app_inputfilename.__name__)
#        app_input_filename = self._get_app_inputfilename(config)
#        self.log.info('Finished %s' % self._get_app_inputfilename.__name__)             
#        self.log.info('Start %s' % self._get_command.__name__)
#        command = self._get_command(prefix=self._command_prefix,input_filename=app_input_filename)   
#        self.log.info('FINISHED %s' % self._get_command.__name__)
#        return command     
    
    def _get_parsed_args(self,args):
        parser = argparse.ArgumentParser(description='Wrapper around a spectra identification application')
        parser.add_argument('-p','--prefix',required=True,nargs=1, action="store", dest="prefix",type=str,help="prefix of the command to execute")
        parser.add_argument('-i','--input',required=True,nargs=1, action="store", dest="input_filename",type=str,help="input file")
        parser.add_argument('-t','--template',required=True,nargs=1, action="store", dest="template_filename",type=str,help="template of the program specific input file")
        parser.add_argument('-o','--output',required=True,nargs=1, action="store", dest="output_filename",type=str,help="output file")
        parser.add_argument('-n','--name',required=False,default=self.name,nargs=1, action="store", dest="name",type=str,help="identifier used in the process")
        a = parser.parse_args(args)
        if type(a.name) is list:
            a.name = a.name[0]
        return {'prefix':a.prefix[0],
                'input_filename':a.input_filename[0],
                'template_filename':a.template_filename[0],
                'output_filename':a.output_filename[0],
                'name':a.name
                }         

    def _validate_parsed_args(self,dict):    
        self._command_prefix = dict['prefix']
        self._input_filename = dict['input_filename']
        self.log.debug("input file [%s]" % os.path.abspath(self._input_filename))
        if not os.path.exists(self._input_filename):
            self.log.fatal('file [%s] does not exist' % self._input_filename)
        self._template_filename = dict['template_filename']
        self.log.debug("template file [%s]" % os.path.abspath(self._template_filename))
        if not os.path.exists(self._template_filename):
            self.log.fatal('file [%s] does not exist' % self._template_filename)
            sys.exit(1)
        self._output_filename = dict['output_filename']
        self.name = dict['name']           
                   
class SequenceTemplateApplication(TemplateApplication):
          
    def _get_parsed_args(self,args):
        parser = argparse.ArgumentParser(description='Wrapper around a spectra identification application')
        parser.add_argument('-p','--prefix',required=True,nargs='+', action="append", dest="prefix",type=str,help="prefix of the command to execute")
        parser.add_argument('-i','--input',required=True,nargs=1, action="store", dest="input_filename",type=str,help="input file")
        parser.add_argument('-t','--template',required=True,nargs=1, action="store", dest="template_filename",type=str,help="template of the program specific input file")
        parser.add_argument('-o','--output',required=True,nargs=1, action="store", dest="output_filename",type=str,help="output file")
        parser.add_argument('-n','--name',required=False,default=self.name,nargs=1, action="store", dest="name",type=str,help="identifier used in the process")
        a = parser.parse_args(args)
        if type(a.name) is list:
            a.name = a.name[0]
        return {'prefix':Utilities().get_flatten_sequence(a.prefix),
                'input_filename':a.input_filename[0],
                'template_filename':a.template_filename[0],
                'output_filename':a.output_filename[0],
                'name':a.name
                } 

               
class CollectorApplication(Application):   
    
    def __call__(self, args):
        "Running the class' main logic and returns the exit code of the validate_run method"      
        self.log.debug('application class file [%s]' % args[0])
        self.log.debug('arguments [%s]' % args[1:])
        self.log.debug('Python class [%s]' % self.__class__.__name__)   
        self.log.info('Start [%s]' % self._get_parsed_args.__name__)
        parsed_args = self._get_parsed_args(args[1:])        
        self.log.info('Finish [%s]' % self._get_parsed_args.__name__)          
        self.log.info('Start [%s]' % self._validate_parsed_args.__name__)
        self._validate_parsed_args(parsed_args)        
        self.log.info('Finish [%s]' % self._validate_parsed_args.__name__)              
        self.log.info('Start [%s]' % self._preprocessing.__name__)
        ini_filenames = self._preprocessing()     
        self.log.info('Finish [%s]' % self._preprocessing.__name__)   
        self.log.info('generated ini files [%s]' % ini_filenames)
        self.log.info('Start [%s]' % self._run.__name__)
        run_code = self._run(ini_filenames)
        self.log.info('Finish [%s]' % self._run.__name__)
        if run_code is not None:
            self.log.info('run_code [%s]' % run_code)        
        self.log.info('Start [%s]' % self._validate_run.__name__)
        exit_code = self._validate_run(run_code)
        self.log.info('Finish [%s]' % self._validate_run.__name__)
        self.log.info('exit_code [%s]' % exit_code)
        return int(exit_code)    
      
    def _get_parsed_args(self,args):
        parser = argparse.ArgumentParser(description='Wrapper around a spectra identification application')
        parser.add_argument('-i','--input',required=True,nargs='+', action="append", dest="input_filenames",type=str,help="input file")
        parser.add_argument('-t','--template',required=True,nargs='+', action="append", dest="template_filenames",type=str,help="template of the program specific input file")
        parser.add_argument('-n','--num',required=False,default=[1], nargs=1, action="store", dest="num_threads",type=int, help="max. number of parallel threads used")
        a = parser.parse_args(args)
        return {
                'input_filenames':Utilities().get_flatten_sequence(a.input_filenames),
                'template_filenames':Utilities().get_flatten_sequence(a.template_filenames),
                'num_threads':a.num_threads[0]
                }
        
    def _preprocessing(self):
        pepxml_by_paramidx = {}
        self._iniFile = None
        param_configs = {}
        for ini_filebasename in self._input_filenames:
            for ini_file in glob.glob("%s*" % (ini_filebasename)):
                self._iniFile = IniFile(input_filename=ini_file, lock=False)
                config = self._iniFile.read_ini()
                idx = config['PARAM_IDX']
                pepxml = config['PEPXML']
                if pepxml_by_paramidx.has_key(idx):
                    pepxml_by_paramidx[idx].append(pepxml)
                else:
                    pepxml_by_paramidx[idx] = [pepxml]
                    param_configs[idx] = config 
        self.log.info('Start %s' % self.create_workdir.__name__)
        self._wd = self.create_workdir(config)
        self.log.info('Finished %s' % self.create_workdir.__name__)
        self.log.warning(param_configs)
        ini_filenames = []
        for k,v in pepxml_by_paramidx.iteritems():
            self.log.debug('[%s] pepxml for param idx [%s]' % (len(v), k))
            for filename in v:
                if not os.path.exists(filename):
                    self.log.fatal('file [%s] does not exist' % filename)
                    sys.exit(1)        
            self.log.debug('all pepxml files exist')
            config = param_configs[k]
            self.log.debug("updated key 'SPECTRA_IDX' with value [%s] in ini" % config['SPECTRA_IDX'])                     
            self.log.debug("updated key 'DIR' with value [%s] in ini" % self._wd)   
            config['DIR'] = self._wd            
            config['SPECTRA_IDX'] = ''
#            config['PARAM_IDX'] = k
            config['PEPXML'] = ','.join(v)
            ini_filename = os.path.join(config['DIR'],k + '.ini')
            IniFile(input_filename=ini_filename).write_ini(config)
            self.log.debug("content of ini file [%s] for param [%s]: %s" % (ini_filename,k,config))
            if not os.path.exists(ini_filename):
                self.log.fatal('file [%s] does not exsist' % ini_filename)
                sys.exit(1)
            ini_filenames.append(ini_filename)
        return ini_filenames
    
    def _run(self,ini_filenames):
        '''
        Exectes the main part of the Application.
        '''
        raise NotImplementedError("Called '_run' method on abstract class")          
               

    def _validate_parsed_args(self,dict):   
        self._input_filenames = dict['input_filenames']
        self._template_filenames = dict['template_filenames']
        self._num_threads = dict['num_threads']             
        self.log.debug("template filenames [%s]" % self._template_filenames)
        self.log.debug(" num of template filenames [%s]" % len(self._template_filenames))
        for filename in self._template_filenames:
            if not os.path.exists(filename):
                self.log.fatal('file [%s] does not exist' % filename)
                sys.exit(1)        
            
    def _validate_run(self,run_code):              
        raise NotImplementedError("Called '_run' method on abstract class")
       
    def create_workdir(self,config):
        wd = None
        try:
            basedir = config['DIR'] 
            wd = os.path.join(basedir,self.name)                       
            self.log.debug('Created workdir [%s]' % wd)
            os.makedirs(wd)

        except Exception,e:
            if os.access( wd, os.F_OK):
                self.log.warning("dir [%s] already exists and can be accessed" % wd)
                self.log.debug('delete old dir')
                shutil.rmtree(wd)
                self.log.debug('create dir')
                os.makedirs(wd)
            else:                
                self.log.warning(e)  
                sys.exit(1) 
        return wd    