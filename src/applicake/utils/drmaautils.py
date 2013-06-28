"""
Created on Aug 17, 2012

@author: lorenz,quandtan

ADD TO .bashrc
module load drmaa
"""

import tempfile

import drmaa


class DrmaaSubmitter(object):
    _session = None

    def __init__(self):
        print "Starting up drmaa session"
        self._session = drmaa.Session()
        self._session.initialize()
        print "DRM Info:", self._session.drmsInfo, "Implempentation:", self._session.drmaaImplementation


    def run(self, executable, commandarray=[], lsfargs='', wdir='.'):
        opath = self._prepare_outfile('.out', wdir)
        epath = self._prepare_outfile('.err', wdir)
        jobinfo = self._runjob(executable, commandarray, lsfargs, opath, epath)
        success = self._validate(jobinfo, opath, epath)
        if not success:
            raise Exception('DRMAA job failed')

    def __del__(self):
        print 'Stopping drmaa session'
        self._session.exit()

    ##########################################################################

    def _prepare_outfile(self, sfx, wdir):
        (_, path) = tempfile.mkstemp(prefix='drmaa', suffix=sfx, dir=wdir)
        return path

    def _runjob(self, executable, commandarray, lsfargs, opath, epath):
        """
        Core for job setup, execution and wait. validation outsourced
        """
        #job template is kind of job container
        jt = self._session.createJobTemplate()
        jt.remoteCommand = executable
        jt.args = commandarray
        #lsfargs is a string to define LSF options (queue, lustre...)
        jt.nativeSpecification = lsfargs
        #force separate stdout stderr
        jt.joinFiles = False
        #DRMAA spec requires ':' in path to separate optional host from filename
        jt.outputPath = ':' + opath
        jt.errorPath = ':' + epath

        print 'Running job ' + executable
        jobid = self._session.runJob(jt)
        jobinfo = self._session.wait(jobid, drmaa.Session.TIMEOUT_WAIT_FOREVER)
        self._session.deleteJobTemplate(jt)
        print 'Finished job ' + executable

        return jobinfo

    def _validate(self, jobinfo, opath, epath):
        if jobinfo.hasExited:
            if int(jobinfo.exitStatus) == 0:
                print "Job finished sucessfully"
                return True
            else:
                print "Job ran but failed with exitcode %d" % int(jobinfo.exitStatus)
        else:
            if jobinfo.hasSignal:
                print "Job aborted with signal %s" % jobinfo.terminatedSignal
            else:
                print "Job aborted manually"

        print "---stdout was---"
        print open(opath, "r").read()
        print "---stderr was---"
        print open(epath, "r").read()

        return False
    
