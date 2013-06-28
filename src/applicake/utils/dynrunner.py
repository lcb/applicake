#!/usr/bin/env python
"""
Created on May 14, 2013

Loads applicake application and runner dynamically from cmd line arguments

Example usage:
DynRunner.run(["applicake.applications.os.echo.Echo","--COMMENT","hello"])

@author: loblum
"""

import importlib
import sys

from applicake.framework.interfaces import IWrapper, IApplication
from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner


class DynRunner(object):
    @staticmethod
    def run(argv):
        #get application class, from http://stackoverflow.com/a/10773699
        try:
            modulearg, classarg = argv[0].rsplit('.', 1)
            module = importlib.import_module(modulearg)
            application = getattr(module, classarg)()
        except:
            raise Exception('Could load application [%s]' % argv[0])

        #get runner
        if isinstance(application, IApplication):
            runner = IniApplicationRunner()
        elif isinstance(application, IWrapper):
            runner = IniWrapperRunner()
        else:
            raise Exception('Could not identfy runner for application [%s]' % argv[0])

            #first arg in argv is usually scriptname, skip it
        exit_code = runner(argv[1:], application)
        if exit_code != 0:
            print 'Execution of applicaton [%s] failed' % argv[0]
            sys.exit(1)