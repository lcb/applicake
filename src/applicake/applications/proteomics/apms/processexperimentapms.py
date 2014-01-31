#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: loblum, quandtan
"""
from configobj import ConfigObj

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication


class ProcessExperimentApms(IApplication):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.SEARCH, 'Key where containing files of downloaded experiment')
        return args_handler

    def main(self, info, log):
        for entry in info[Keys.SEARCH]:
            if entry.endswith('.properties'):
                propfile = entry

        propinfo = ConfigObj(propfile)
        info['PEPCSV'] = propinfo['PEPCSV']
        info['DBASE'] = propinfo['DBASE']

        #remove these guys to prevent parameter sweep
        info[Keys.SEARCH] = None
        info[Keys.DSSOUTPUT] = None
        return 0, info
