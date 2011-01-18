#!/usr/bin/env python


'''
Created on Dec 19, 2010

@author: quandtan
'''


import sys,logging
from applicake.app import ExternalApplication as app

# init the application object (__init__)
a = app(use_filesystem=False,name=None)
# call the application object as method (__call__)

exit_code = a(sys.argv)
print(exit_code)
sys.exit(exit_code)
