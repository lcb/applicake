#!/usr/bin/env python


'''
Created on Dec 19, 2010

@author: quandtan
'''

import sys,os,shutil
from applicake.app import ExternalApplication as app

## init the application object (__init__)
#a = app(use_filesystem=False,name=None)
#print sys.argv
#exit_code = a(sys.argv)
##copy the log file to the working dir
##for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
##    shutil.move(filename, os.path.join(a._wd,filename))
#print(exit_code)
#sys.exit(exit_code)




# test of the Thread pool
from random import randrange
from applicake.utils import ThreadPool

delays = [randrange(1, 10) for i in range(100)]

from time import sleep
def wait_delay(d):
    print 'sleeping for (%d)sec' % d
    sleep(d)

# 1) Init a Thread pool with the desired number of threads
pool = ThreadPool(20)

for i, d in enumerate(delays):
    # print the percentage of tasks placed in the queue
    print '%.2f%c' % ((float(i)/float(len(delays)))*100.0,'%')
    
    # 2) Add the task to the queue
    pool.add_task(wait_delay, d)

# 3) Wait for completion
pool.wait_completion()