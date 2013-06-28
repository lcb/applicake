#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: loblum, quandtan
"""

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication


class ProcessExperiment(IApplication):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.SEARCH, 'Key where containing files of downloaded experiment')
        args_handler.add_app_args(log, 'GETCODES', 'Get DSS codes from experiment properties', action='store_true',
                                  default=False)
        return args_handler

    def main(self, info, log):
        for entry in info[Keys.SEARCH]:
            #official 'regex' from ch/systemsx/cisd/openbis/etlserver/proteomics/ProtXMLUploader.java
            #no starting dot, all lowercase
            if entry.endswith('prot.xml'):
                info[Keys.PROTXML] = entry
            if entry.endswith('pep.xml'):
                info[Keys.PEPXMLS] = [entry]
            if entry.endswith('.properties'):
                propfile = entry

        run_code = 0
        if not Keys.PROTXML in info:
            log.fatal("No prot xml file was found")
            run_code = 1
        if not Keys.PEPXMLS in info:
            log.fatal("No pep xml file was found")
            run_code = 1

        if info['GETCODES']:
            with open(propfile) as prop:
                for line in prop.readlines():
                    if line.startswith("PARENT-DATA-SET-CODES"):
                        info[Keys.DATASET_CODE] = line.split('=')[1].strip().split(', ')
            if Keys.DATASET_CODE not in info:
                log.fatal("No search properties file was found in experiment folder")
                run_code = 1

        #remove these guys to prevent parameter sweep
        info[Keys.SEARCH] = None
        info[Keys.DSSOUTPUT] = None
        return run_code, info
