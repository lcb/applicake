#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: loblum
'''

import os
from applicake.framework.interfaces import IWrapper

class GetExperiment(IWrapper):
    
    _outfile = 'getexperiment.out'
        
    def set_args(self,log,args_handler):  
        args_handler.add_app_args(log, self.DATASET_DIR, 'Dir to store datasets')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the Echo executable')
        args_handler.add_app_args(log, 'EXPERIMENT', 'Experiment to donwload and get datasets from')
        return args_handler
    
    def prepare_run(self,info,log):
        if self.PREFIX in info:
            prefix = info[self.PREFIX]
        else:
            prefix = 'getexperiment'
        experiment = info['EXPERIMENT']
        datasetdir = os.path.join(info[self.DATASET_DIR],experiment)
        
        cmd = "%s --result=%s --out=%s -f -v %s" % (prefix,self._outfile,datasetdir,experiment)
        return (cmd,info)
    
    def validate_run(self,info,log,run_code, out_stream, err_stream): 
        with open(self._outfile) as result:
            for line in result.readlines():
                if line.startswith(info['EXPERIMENT']):
                    fname = line.split('\t')[1].strip()
                    if fname.lower().endswith('.pep.xml'):
                        info["PEPXML_FILE"] = fname
                    if fname.lower().endswith('.prot.xml'):
                        info["PROTXML_FILE"] = fname
                    if fname.lower().endswith('.properties'):
                        info["SEARCH_PROPS"] = fname
                    
        if not "PEPXML_FILE" in info:
            log.fatal("No pep xml file was found")
            run_code = 1
        if not "PROTXML_FILE" in info:
            log.fatal("No prot xml file was found")
            run_code = 1
        if not "SEARCH_PROPS" in info:
            log.fatal("No search properties file was found in experiment folder")
            run_code = 1
                        
        with open(info["SEARCH_PROPS"]) as prop:
            for line in prop.readlines():
                if line.startswith("PARENT-DATA-SET-CODES"):
                    info[self.DATASET_CODE] = line.split('=')[1].strip()
        
        if not self.DATASET_CODE in info:
            log.fatal("No search properties file was found in experiment folder")
            run_code = 1
            
        return (run_code,info) 