#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: loblum
'''

from applicake.framework.interfaces import IApplication

class ProcessExperiment(IApplication):

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'EXPERIMENTFILES', 'Experiment to donwload and get datasets from')
        args_handler.add_app_args(log, 'MSFILES', 'MS data used for next dss')
        return args_handler

    def main(self,info,log):
        for entry in info['EXPERIMENTFILES']:
            #official 'regex' from ch/systemsx/cisd/openbis/etlserver/proteomics/ProtXMLUploader.java
            #no starting dot, all lowercase
            if entry.endswith('prot.xml'):
                info["PROTXML_FILE"] = entry
            if entry.endswith('pep.xml'):
                info["PEPXML_FILE"] = entry

        run_code = 0
        if not "PEPXML_FILE" in info:
            log.fatal("No pep xml file was found")
            run_code = 1
        if not "PROTXML_FILE" in info:
            log.fatal("No prot xml file was found")
            run_code = 1

        info[self.DATASET_CODE] = info['MSFILES']

        info['EXPERIMENTFILES'] = None
        info['MSFILES'] = None
        return (run_code,info)