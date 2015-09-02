#!/usr/bin/env python
from applicake.app import BasicApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys
import re


class ProcessExperiment(BasicApp):
    def add_args(self):
        return [
            Argument('SEARCH', 'Key where containing files of downloaded experiment')
        ]

    def run(self, log, info):
        for entry in info['SEARCH']:
            #official 'regex' from ch/systemsx/cisd/openbis/etlserver/proteomics/ProtXMLUploader.java
            #no starting dot, all lowercase
            if entry.endswith('prot.xml'):
                info[Keys.PROTXML] = entry
            if entry.endswith('pep.xml'):
                info[Keys.PEPXML] = entry
            if re.match(".*_main_1.0..csv",entry):
                info['MAYUOUT'] = entry
            if entry.endswith('.properties'):
                propfile = entry

        if not Keys.PROTXML in info:
            raise RuntimeError("No prot xml file was found")
        if not Keys.PEPXML in info:
            raise RuntimeError("No pep xml file was found")

        return info

if __name__ == "__main__":
    ProcessExperiment.main()