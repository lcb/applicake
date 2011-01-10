#!/usr/bin/env python
'''
Created on Dec 19, 2010

@author: quandtan
'''

import sys,os,getopt,traceback,shutil,argparse
from applicake.utils import Utilities,Generator,IniFile
from applicake.app import Application

class WorkflowInitiator(Application):     
    
    def _create_jobdir(self):
        self.log.debug('get job_id....')
        jobid = str(Generator().job_id(self._dirname))
        self.log.debug('job_id [%s]' % jobid)
        job_dirname = os.path.join(self._dirname,jobid)                 
        os.mkdir(job_dirname)
        if(os.path.exists(job_dirname)):
            self.log.debug('job_dir [%s] was created.' % job_dirname)
        else:
            self.log.fatal('job_dir [%s] was not created.' % job_dirname)
            sys.exit(1)
        return job_dirname
         
    def _get_parsed_args(self):
        parser = argparse.ArgumentParser(description='Script which initiates a workflow')
        parser.add_argument('-i','--input', action="store", dest="input",type=str,help="input file")
        parser.add_argument('-c','--config', action="store", dest="config",type=str,help="config file")
        parser.add_argument('-d','--dir', action="store", dest="dir",type=str,help="base directory")
        a = parser.parse_args()
        return {'input_filename':a.input,'config_filename':a.config,'dirname':a.dir}                          
            
    def _preprocessing(self):
        self.log.debug('method has no real implementation')                                           
                
    def _run(self,command=None):
        try:
            print(os.path.abspath(self._log_filename))
            self.log.info('Start [%s]' % self._create_jobdir.__name__)
            job_dirname = self._create_jobdir()
            self.log.info('Finished [%s]' % self._create_jobdir.__name__)    
            
            
#            out_filename = os.path.join(job_dirname,os.path.split(self._config_filename)[1])
#            ini_file = IniFile(in_filename=self._config_filename,out_filename=out_filename,lock=False)    
            ini_file = IniFile(input_filename=self._config_filename,lock=False) 

            
            self.log.debug('Start [%s]' % ini_file.read_ini.__name__)
            config = ini_file.read_ini()
            self.log.debug('Finished [%s]' % ini_file.read_ini.__name__)
            config.update({'DIR':job_dirname})
            self.log.debug("add DIR to config file content in memory")
            self.log.debug('Start [%s]' % ini_file.write_ini_value_product.__name__)
            param_filenames = ini_file.write_ini_value_product(config=config,use_subdir=False,index_key="PARAM_IDX")
            self.log.debug('generated [%s] parameter files' % len(param_filenames))
            self.log.debug('Finished [%s]' % ini_file.write_ini_value_product.__name__)
            self.log.debug('start generating output files (parameter x spectra files) and delete original parameter file')
            path_config = IniFile(input_filename=self._input_filename).read_ini()
            self._output_filenames = []
            for param_filename in param_filenames:
                ini = IniFile(input_filename=param_filename,lock=False)
                config = ini.read_ini()
                config.update(path_config)
                out_filenames = ini.write_ini_value_product(config=config,use_subdir=False,index_key="SPECTRA_IDX")
                self._output_filenames.extend(out_filenames)
                os.remove(param_filename)
            self.log.debug('generated [%s] output files' % len(self._output_filenames))
            self.log.debug('finished adding paths to each output file') 
            return 0
        except Exception,e:
            self.log.exception(e)
            return 1        
            
    def _validate_parsed_args(self,dict):
        if dict['input_filename'] is None:
            self.log.fatal('argument [input] was not set')
            sys.exit(1)
        else:
            self._input_filename = dict['input_filename']
            if not os.path.exists(self._input_filename):
                self.log.fatal('file [%s] does not exist' % self._input_filename)
        if dict['config_filename'] is None:
            self.log.fatal('argument [config] was not set')
            sys.exit(1)
        else:
            self._config_filename = dict['config_filename']
            if not os.path.exists(self._config_filename):
                self.log.fatal('file [%s] does not exist' % self._config_filename)
        if dict['dirname'] is None:
            self.log.fatal('argument [dir] was not set')
            sys.exit(1)
        else:
            self._dirname = dict['dirname']
            if not os.path.exists(self._dirname):
                self.log.fatal('file [%s] does not exist' % self._dirname)                  
            
    def _validate_run(self,run_code=None):
        if 0 < run_code:
            return run_code 
        if len(self._output_filenames) == 0: 
            self.log.error('No output files generated.')
            return 1
        for filename in self._output_filenames:
            if not os.path.exists(filename):
                self.log.fatal('File [%s] does not exist' % os.path.abspath(filename))
                return 1
            else:
                self.log.debug('File [%s] does exist' % os.path.abspath(filename))                
        return 0       
            

if __name__ == '__main__':    
    a = WorkflowInitiator(use_filesystem=True)
    exit_code = a(sys.argv)
    print(exit_code)
    sys.exit(exit_code)
   
   
    

   
