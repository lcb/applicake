#!/usr/bin/env python


'''
Created on Dec 19, 2010

@author: quandtan
'''


import sys,logging
from applicake.app import SimpleApplication as app
from utils import Generator as gen
import fcntl

# init the application object (__init__)
a = app(use_filesystem=True,name='bla')
# call the application object as method (__call__)
print(gen().job_id('/tmp'))

exit_code = a(sys.argv)
print(exit_code)
sys.exit(exit_code)
