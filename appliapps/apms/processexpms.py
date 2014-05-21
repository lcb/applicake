#!/usr/bin/env python
from configobj import ConfigObj

from applicake.app import BasicApp
from applicake.coreutils.arguments import Argument


class ProcessExperimentApms(BasicApp):
    def add_args(self):
        return [
            Argument('SEARCH', 'Key where containing files of downloaded experiment')
        ]

    def run(self, log, info):
        for entry in info['SEARCH']:
            if entry.endswith('peptides.tsv'):
                info['PEPCSV'] = entry
            if entry.endswith('.properties'):
                propfile = entry

        propinfo = ConfigObj(propfile)
        info['DBASE'] = propinfo['DBASE']

        return info

if __name__ == "__main__":
    ProcessExperimentApms.main()