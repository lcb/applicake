'''
Created on Aug 17, 2012

@author: lorenz,quandtan

ADD TO .bashrc
module load drmaa
export PYTHONPATH=/cluster/apps/imsbtools/stable/pythonlibs/python-drmaa:$PYTHONPATH
'''

import drmaa
import tempfile
import os

class DrmaaSubmitter(object):
    _session = None
    
    def __init__(self):       
        print 'Starting up drmaa session'        
        self._session = drmaa.Session()
        #print 'Supported contact strings: ' + self._session.contact
        print 'Supported DRM systems: ' + str(self._session.drmsInfo)
        print 'Supported DRMAA implementations: ' + str(self._session.drmaaImplementation)         
        self._session.initialize()
        
    def run(self,executable,commandarray=[],lsfargs='',wdir='.'):
        #job template is kind of job container
        jt = self._session.createJobTemplate()
        jt.remoteCommand = executable
        jt.args = commandarray
        #lsfargs is a string to define LSF options (queue, lustre...)
        jt.nativeSpecification = lsfargs
        #force separate stdout stderr
        jt.joinFiles = False  
        #DRMAA spec requires ':' in path to separate optional host from filename
        (handle,opath) = tempfile.mkstemp(prefix='drmaa',suffix='.out',dir=wdir)
        jt.outputPath = ":" + opath
        (handle,epath) = tempfile.mkstemp(prefix='drmaa',suffix='.err',dir=wdir)
        jt.errorPath = ":" + epath
        
        print 'Running job ' + executable
        jobid = self._session.runJob(jt)
        jobinfo = self._session.wait(jobid, drmaa.Session.TIMEOUT_WAIT_FOREVER)
        self._session.deleteJobTemplate(jt)
        print 'Finished job ' + executable
        
#        return (jobinfo,opath,epath)
#            
#    def validated_run(self,executable,commandarray=[],lsfargs='',wdir='.'):
#        (jobinfo,opath,epath) = self.run(executable, commandarray, lsfargs, wdir)
        
        print "===stdout was==="
        print open(opath, "r").read()
        os.remove(opath)
        print "===stderr was==="
        print open(epath, "r").read()
        os.remove(epath)
        
        if jobinfo.hasExited:
            if int(jobinfo.exitStatus) == 0:
                print "Job ran and finished sucessfully"
                return
        if jobinfo.hasExited:
                print "Job ran but failed with exitcode %d" % jobinfo.exitStatus
                raise
        else:
            if jobinfo.hasSignal:
                print "Job aborted with signal %s" %  jobinfo.terminatedSignal 
                raise
            else:
                print "Job aborted manually"
                raise  
    
    def __del__(self):
        print 'Stopping drmaa session'
        self._session.exit()
