#!/usr/bin/env python


'''
Created on Dec 19, 2010

@author: quandtan
'''


import sys,os,shutil
from applicake.app import ExternalApplication as app

# init the application object (__init__)
a = app(use_filesystem=False,name=None)
exit_code = a(sys.argv)
#copy the log file to the working dir
#for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
#    shutil.move(filename, os.path.join(a._wd,filename))
print(exit_code)
sys.exit(exit_code)