#!/usr/bin/env python
'''
Created on Dec 19, 2010

@author: quandtan
'''

import sys,os,getopt,traceback,shutil,argparse
from applicake.utils import Workflow,IniFile
from applicake.app import Application

class WorkflowInitiator(Application):     
    
    def _create_jobdir(self):
        self.log.debug('get_jobid....')
        jobid = str(Workflow().get_jobid(self._dirname))
        self.log.debug('get_jobid [%s]' % jobid)
        job_dirname = os.path.join(self._dirname,jobid)                 
        os.mkdir(job_dirname)
        if(os.path.exists(job_dirname)):
            self.log.debug('job_dir [%s] was created.' % job_dirname)
        else:
            self.log.fatal('job_dir [%s] was not created.' % job_dirname)
            sys.exit(1)
        return job_dirname,jobid      
         
    def _get_parsed_args(self,args):
        parser = argparse.ArgumentParser(description='Script which initiates a workflow')
        parser.add_argument('-i','--input', required=True,nargs=1,action="store", dest="input_filename",type=str,help="input file")
        parser.add_argument('-c','--config', required=True,nargs=1,action="store", dest="config_filename",type=str,help="config file")
        parser.add_argument('-d','--dir', required=True,nargs=1,action="store", dest="dirname",type=str,help="base directory")
        a = parser.parse_args(args)
        return {'input_filename':a.input_filename[0],'config_filename':a.config_filename[0],'dirname':a.dirname[0]}                          
            
    def _preprocessing(self):
        self.log.info('Start %s' % self._create_jobdir.__name__)
        self._wd,jobid = self._create_jobdir()
        self.log.info('Finished %s' % self._create_jobdir.__name__)   
        self._iniFile = IniFile(input_filename=self._config_filename,lock=False) 
#        self.log.debug('Start [%s]' % self._iniFile.read_ini.__name__)
#        config = self._iniFile.read_ini()
#        self.log.debug('Finished [%s]' % self._iniFile.read_ini.__name__)
        self._iniFile.add_to_ini({'DIR':self._wd,'JOBID':jobid})
        self.log.debug("add key 'DIR' with value [%s] to ini" % self._wd)
        self.log.debug("add key 'JOBID' with value [%s] to ini" % jobid)
                
#    def _run(self,command=None):
#        try:
#            self.log.debug('Start [%s]' % self._iniFile.write_ini_value_product.__name__)  
#            param_filenames = self._iniFile.write_ini_value_product(config=self._iniFile.read_ini(),use_subdir=False,sep='',index_key="PARAM_IDX")
#            self.log.debug('generated [%s] parameter files' % len(param_filenames))
#            self.log.debug('Finished [%s]' % self._iniFile.write_ini_value_product.__name__)
#            self.log.debug('start generating output files (parameter x spectra files) and delete original parameter file')
#            path_config = IniFile(input_filename=self._input_filename).read_ini()            
#            self._output_filenames = []
#            for param_filename in param_filenames:
#                ini = IniFile(input_filename=param_filename,lock=False)
#                config = ini.read_ini()
#                config.update(path_config)
#                out_filenames = ini.write_ini_value_product(config=config,use_subdir=False,sep = config['PGSEP'],index_key="SPECTRA_IDX")
#                # add DATASET_CODE from path_config as PARENT-DATA-SET-CODES (has to be done after the product writing ;-)
#                for out_filename in out_filenames:
#                    ini = IniFile(input_filename=out_filename,lock=False)
#                    parent_dataset_codes = ','.join(path_config['DATASET_CODE'])
##                    ini.add_to_ini({'PARENT-DATA-SET-CODES':parent_dataset_codes}) 
#                    ini.add_to_ini({'PARENT-DATA-SET-CODES':path_config['DATASET_CODE']})
#                self._output_filenames.extend(out_filenames)
#                os.remove(param_filename)
#            self.log.debug('generated [%s] output files' % len(self._output_filenames))
#            self.log.debug('finished adding paths to each output file') 
#            return 0
#        except Exception,e:
#            self.log.exception(e)
#            return 1        


    def _run(self,command=None):
        try:
            self.log.debug('Start [%s]' % self._iniFile.write_ini_value_product.__name__)  
            # the use of a fileidx is needed for guse as this workflowmanager requires a continous index    
            config = self._iniFile.read_ini()
            # the sep has to be some unusual separator
            tmpsep = '...'
            param_filenames,endidx = self._iniFile.write_ini_value_product(config=config,use_subdir=False,sep=tmpsep,index_key="PARAM_IDX")
            self.log.debug('generated [%s] parameter files' % len(param_filenames))
            self.log.debug('Finished [%s]' % self._iniFile.write_ini_value_product.__name__)
            self.log.debug('start generating output files (parameter x spectra files) and delete original parameter file')
            path_config = IniFile(input_filename=self._input_filename).read_ini()            
            self._output_filenames = []
            fileidx = 0
            for idx,param_filename in enumerate(param_filenames):
                ini = IniFile(input_filename=param_filename,lock=False)
                config = ini.read_ini()
                config.update(path_config)
                fname = os.path.abspath(param_filename).rstrip('%s%s' % (tmpsep,idx)) 
                out_filenames,fileidx = ini.write_ini_value_product(config=config,use_subdir=False,fname=fname, sep=config['PGSEP'],index_key="SPECTRA_IDX",fileidx=fileidx)
                # add DATASET_CODE from path_config as PARENT-DATA-SET-CODES (has to be done after the product writing ;-)
                for out_filename in out_filenames:
                    ini = IniFile(input_filename=out_filename,lock=False)
                    parent_dataset_codes = ','.join(path_config['DATASET_CODE'])
#                    ini.add_to_ini({'PARENT-DATA-SET-CODES':parent_dataset_codes}) 
                    ini.add_to_ini({'PARENT-DATA-SET-CODES':path_config['DATASET_CODE']})
                self._output_filenames.extend(out_filenames)
                os.remove(param_filename)
            self.log.debug('generated [%s] output files' % len(self._output_filenames))
            self.log.debug('finished adding paths to each output file') 
            return 0
        except Exception,e:
            self.log.exception(e)
            return 1 

            
    def _validate_parsed_args(self,dict):
        self._input_filename = dict['input_filename']
        if not os.path.exists(self._input_filename):
            self.log.fatal('file [%s] does not exist' % self._input_filename)
        self._config_filename = dict['config_filename']
        if not os.path.exists(self._config_filename):
            self.log.fatal('file [%s] does not exist' % self._config_filename)
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
   
   
    

   
