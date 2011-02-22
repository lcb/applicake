#!/usr/bin/env python


'''
Created on Dec 19, 2010

@author: quandtan
'''

import sys,os,shutil,time
from applicake.app import ExternalApplication as app
#-----------------------------------------------------------------------------
#from numpy import arange,sqrt, random, linalg
#from multiprocessing import Pool
#
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
#a = time.clock()
#po = Pool(1)
#for i in xrange(1,3000):
#    j = random.normal(1,1,(100,100))
#    po.apply_async(det,(j,),callback=cb)
##    po.apply_async(f,(i,))
#po.close()
#po.join()
#print counter
#b = time.clock()
#print b -a

#-----------------------------------------------------------------------------

#import time
#from multiprocessing import Process,Queue
#from Queue import Empty
#class Test(object):
#    def f(self,x):
#        print x*x
#        time.sleep(2)        
#    def run(self):
#        q = Queue(4)
#        procs = [Process(target=self.f,args=(i,)) for i in range(100)]
#        for p in procs:
#            p.start()         
#        for p in procs:
#            p.join() 
#        
#        
#if "__main__" == __name__:
#    t=Test()
#    t.run()        

#-----------------------------------------------------------------------------
           
## {{{ http://code.activestate.com/recipes/577187/ (r9)
#from Queue import Queue
#from threading import Thread
#
#class Worker(Thread):
#    """Thread executing tasks from a given tasks queue"""
#    def __init__(self, tasks):
#        Thread.__init__(self)
#        self.tasks = tasks
#        self.daemon = True
#        self.start()
#    
#    def run(self):
#        while True:
#            func, args, kargs = self.tasks.get()
#            try: func(*args, **kargs)
#            except Exception, e: print e
#            self.tasks.task_done()
#
#class ThreadPool:
#    """Pool of threads consuming tasks from a queue"""
#    def __init__(self, num_threads):
#        self.tasks = Queue(num_threads)
#        for _ in range(num_threads): Worker(self.tasks)
#
#    def add_task(self, func, *args, **kargs):
#        """Add a task to the queue"""
#        self.tasks.put((func, args, kargs))
#
#    def wait_completion(self):
#        """Wait for completion of all the tasks in the queue"""
#        self.tasks.join()

#if __name__ == '__main__':
#    a = time.clock()
#    from random import randrange
#    delays = [randrange(1, 10) for i in range(100)]
#    
#    from time import sleep
#    def wait_delay(d):
#        print 'sleeping for (%d)sec' % d
#        sleep(d)
#    
#    # 1) Init a Thread pool with the desired number of threads
#    pool = ThreadPool(10)
#    
#    for i, d in enumerate(delays):
#        # print the percentage of tasks placed in the queue
#        print '%.2f%c' % ((float(i)/float(len(delays)))*100.0,'%')
#        
#        # 2) Add the task to the queue
#        pool.add_task(wait_delay, d)
#    
#    # 3) Wait for completion
#    pool.wait_completion()
#    b = time.clock()
#    print b -a
## end of http://code.activestate.com/recipes/577187/ }}}

#-----------------------------------------------------------------------------
# works!!!

#from utils import ThreadPool
#class Test(object):
#    
#    def __call__(self):
#        self.run(range(self._num))
#            
#    def __init__(self,x):
#        self._num = x
#            
#    def mul(self,x):
#        from time import sleep
#        if x == 7: self._exit_code = 1
#        if self._exit_code != 1:
#            print x*x
#            sleep(x)
#            print x*x*x
#            sleep(x/5)
#            print '%s finished' % x
#        
#        
#    def run(self,range):
#        a = time.asctime()      
#        self._exit_code = 0
#        pool = ThreadPool(self._num)        
#        for i in range:            
#            pool.add_task(self.mul, i)
#        pool.wait_completion()
#        b = time.asctime()
#        print self._exit_code
#        print "%s:%s" %(a,b)
#            
#if __name__ == '__main__':
#    t = Test(10)
#    print "start"
#    t()
#    
##-----------------------------------------------------------------------------    
data = [1,7,1,1,3,3,4,5]
uniq_peps = list(set(data))
print uniq_peps
    
             