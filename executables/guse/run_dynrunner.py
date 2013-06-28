#!/usr/bin/env python2.7
'''
Created on May 14, 2013

Loads applicake application and runner dynamically from cmd line arguments

Example usage:
cmdline: dynrunner.py applicake.applications.os.echo.Echo --COMMENT hello --PREFIX /bin/echo

@author: loblum
'''
import sys
from applicake.utils.dynrunner import DynRunner

#skip first argument because its name of script (and second will be modulename)
DynRunner.run(sys.argv[1:])