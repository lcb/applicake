#!/usr/bin/env python
'''
Created on Mar 20, 2012

@author: quandtan
'''

import os
import sys
from applicake.framework.runner import ApplicationRunner
from applicake.framework.interfaces import IApplication
from applicake.framework.utils import FileLocker

class Initiator(IApplication):
    """
    Generates a work directory in a specified base directory 
    based on a unique job index.
    """
    
    def _check_dir(self,dir):
        """
        Validate a directory
        
        Arguments:
        - dir: directory path to check
        """
        fail1 = not os.path.exists(dir)
        fail2 = not os.path.isdir(dir)
        fail3 = not os.access(dir,os.R_OK)
        fail4 = not os.access(dir,os.W_OK)
        fails = [fail1,fail2,fail3,fail4]
        if any(fails):
            msg = '''dir [%s] does not exist [%s], 
            is not a dir [%s], cannot be read [%s] or
            cannot be written [%s]''' % (
                                                            os.path.abspath(dir),
                                                            fail1,fail2,fail3,fail4
                                                            )
            self.log.critical(msg)
            sys.exit(1)
        self.log.debug('file [%s] checked successfully' % dir)  
    
    def _get_jobidx(self,dir):
        """
        Generate a unique job index
        
        Arguments:
        - dir: directory where the index file is located.
        
        Return:
        unique job index        
        """
        'Return a unique job id'
        jobid = 1
        filename = os.path.join(dir, 'jobidx.txt')
        locker = FileLocker()
        if (os.path.exists(filename)):            
            fh = open(filename,'r') 
            locker.lock(fh,locker.LOCK_EX) 
            jobid= int(fh.read())   
            jobid += 1         
        fh = open(filename,'w')    
        fh.write(str(jobid))
        locker.unlock(fh)            
        return jobid      
    
    def main(self,config,log):
        key = 'DIR'
        if not config.haskey(key):
            log.error('config [%s] did not contain key [%s]' % (config,key))
            return 1
        else:
            dir = config[key]
            self._check_dir(dir)
            log.info('Start [%s]' % self._get_jobidx.__name__)
            job_idx = self._get_jobidx(dir)
            log.info('Finished [%s]' % self._get_jobidx.__name__)
            log.debug('job_idx [%s]' % job_idx)            
            job_dir = os.path.join(dir,job_idx)                 
            os.mkdir(job_dir)
            if(os.path.exists(job_dir)):
                self.log.debug('job_dir [%s] was created.' % job_dir)
            else:
                self.log.error('job_dir [%s] was not created.' % job_dir)
                return 1
            
if __name__ == '__main__':
    runner = ApplicationRunner()
    application = Initiator()
    exit_code = runner(sys.argv,application)    
    print(exit_code)
    sys.exit(exit_code)            