#!/usr/bin/env python2.7
"""
Executes main() function of class defined in argv[0]
Potentially unsafe but convenient.

Example usage:
dynrunner.py appliapps.os.echo --COMMENT hello
"""
import importlib
import inspect
import sys

appliapp = None
cls = None
try:
    appliapp = sys.argv[1]
    #load app module, from http://stackoverflow.com/a/10773699
    module = importlib.import_module(appliapp)
    #find main class http://stackoverflow.com/q/1796180/
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and appliapp in obj.__module__:
            cls = obj
except Exception, e:
    raise Exception('Could not find/load app [%s]: %s' % (appliapp, e.message))
try:
    cls.main()
except Exception, e:
    raise Exception('Could not run app [%s]: %s' % (appliapp, e.message))