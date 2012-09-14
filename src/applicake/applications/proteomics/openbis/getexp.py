#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: loblum
'''

from applicake.framework.interfaces import IWrapper

class GetExperiment(IWrapper):
    
    def set_args(self,log,args_handler):  
        args_handler.add_app_args(log, self.DATASET_DIR, 'Dir to store datasets')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the Echo executable')
        return args_handler
    
    def prepare_run(self,info,log):
        if self.PREFIX in info:
            prefix = info[self.PREFIX]
        else:
            prefix = "getexperiment"
        datasetdir = info[self.DATASET_DIR]
        experiment = info['EXPERIMENT']
        
        cmd = "%s --out=%s -f -v %s" % (prefix,datasetdir,experiment)
        return (cmd,info)
    
    def validate_run(self,info,log,run_code, out_stream, err_stream): 
        with open("getexperiment.out") as result:
            for line in result.readlines():
                if line.startswith(info['EXPERIMENT']):
                    lowfilename = line.split('\t')[1].strip().lower()
                    if lowfilename.endswith('.pep.xml'):
                        info["PEPXML_FILE"] = lowfilename
                    if lowfilename.endswith('.prot.xml'):
                        info["PROTXML_FILE"] = lowfilename
                    if lowfilename.endswith('.properties'):
                        info["SEARCH_PROPS"] = lowfilename
                    
        if not "PEPXML_FILE" in info:
            log.fatal("No pep xml file was found")
        if not "PROTXML_FILE" in info:
            log.fatal("No prot xml file was found")
        if not "SEARCH_PROPS" in info:
            log.fatal("No search properties file was found in experiment folder")

        with open(info["SEARCH_PROPS"]) as prop:
            for line in prop.readlines():
                if line.startswith("PARENT-DATA-SET-CODES"):
                    info[self.DATASET_CODE] = line.split('=')[1].strip()
        
        if not self.DATASET_CODE in info:
            log.fatal("No search properties file was found in experiment folder")
            
        return (run_code,info)  
