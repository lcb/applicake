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




## test of the Thread pool
#from random import randrange
#from applicake.utils import ThreadPool
#
#delays = [randrange(1, 10) for i in range(100)]
#
#from time import sleep
#def wait_delay(d):
#    print 'sleeping for (%d)sec' % d
#    sleep(d)
#
## 1) Init a Thread pool with the desired number of threads
#pool = ThreadPool(20)
#
#for i, d in enumerate(delays):
#    # print the percentage of tasks placed in the queue
#    print '%.2f%c' % ((float(i)/float(len(delays)))*100.0,'%')
#    
#    # 2) Add the task to the queue
#    pool.add_task(wait_delay, d)
#
## 3) Wait for completion
#pool.wait_completion()

from numpy import arange,sqrt, random, linalg
from multiprocessing import Pool

#global counter
#counter = 0
#
#def cb(r):
#    global counter
#    print counter, r
#    counter +=1
#    
#def det(M):
#    return linalg.det(M)
#
#
#po = Pool(3)
#for i in xrange(1,300):
#    j = random.normal(1,1,(100,100))
#    po.apply_async(det,(j,),callback=cb)
##    po.apply_async(f,(i,))
#po.close()
#po.join()
#print counter

#
import time
from multiprocessing import Process,Queue
from Queue import Empty
class Test(object):
    def f(self,x):
        print x*x
        time.sleep(2)
        

    def run(self):
        q = Queue(4)
        procs = [Process(target=self.f,args=(i,)) for i in range(100)]
        for p in procs:
            p.start()         
        for p in procs:
            p.join() 
        
        
if "__main__" == __name__:
    t=Test()
    t.run()        