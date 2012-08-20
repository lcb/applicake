'''
Created on Aug 17, 2012

@author: lorenz

ADD TO .bashrc
module load drmaa
export PYTHONPATH=/cluster/apps/imsbtools/stable/pythonlibs/python-drmaa:$PYTHONPATH
'''

import drmaa

class DrmaaSubmitter(object):
    _session = None
    
    def __init__(self):
        print 'Starting up drmaa session'
        self._session = drmaa.Session()
        self._session.initialize()
        
    def run(self,specifications,executable,commandarray=[]):
        jt = self._session.createJobTemplate()
        jt.nativeSpecifications(specifications)
        jt.remoteCommand = executable
        jt.args = commandarray
        
        print 'Running ' + executable
        jobid = self._session.runJob(jt)
        retval = self._session.wait(jobid, drmaa.Session.TIMEOUT_WAIT_FOREVER)
        retcode = retval.exitStatus
        self._session.deleteJobTemplate(jt)
        print 'Finished ' + executable + ' ' + jobid 
        
        return retcode
    
    def __del__(self):
        print 'Stopping drmaa session'
        self._session.exit()
