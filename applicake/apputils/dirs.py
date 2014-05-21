import errno
import os
import re
import shutil
import time

from applicake.coreutils.keys import Keys


def create_workdir(log, info):
    if not Keys.WORKDIR in info:
        log.debug("No WORKDIR requested")
        return info

    if info[Keys.WORKDIR] != "":
        log.debug("Using specified WORKDIR [%s]" % info[Keys.WORKDIR])
        return info

    #No workdir specified, creating one using BASEDIR, JOB_IDX, SUBJOBLIST, NAME
    if info.get(Keys.JOB_ID, "") == "":
        info[Keys.JOB_ID] = create_unique_jobdir(info[Keys.BASEDIR])
        log.debug("JOB_ID was not set, generated [%s]" % info[Keys.JOB_ID])

    wd = ''
    for key in [Keys.BASEDIR, Keys.JOB_ID]:
        if key in info:
            wd += info[key] + os.path.sep

    if info.get(Keys.SUBJOBLIST, "") != "":
        if not isinstance(info[Keys.SUBJOBLIST], list):
            info[Keys.SUBJOBLIST] = [info[Keys.SUBJOBLIST]]
        for subjob in info[Keys.SUBJOBLIST]:
            ds = re.sub("\W", "", subjob.split(Keys.SUBJOBSEP)[0]) + '_' + subjob.split(Keys.SUBJOBSEP)[1]
            wd += ds + os.path.sep

    wd += info[Keys.NAME] + os.path.sep
    makedirs_clean(wd)
    log.debug("Created WORKDIR [%s]" % wd)
    info[Keys.WORKDIR] = wd

    return info


def makedirs_clean(wd):
    if os.path.exists(wd):
        shutil.rmtree(wd)
    os.makedirs(wd)
    os.chmod(wd, 0775)


def create_unique_jobdir(basedir):
    #dirname using timestamp, principle from tempfile.mkdtemp()
    #limits: longer foldername if >1 dir/min error on >1000 dir/min
    dirname = time.strftime("%y%m%d%H%M")
    ext = ""
    for i in range(0, 1000):
        try:
            path = os.path.join(basedir, dirname + ext)
            os.mkdir(path)
            os.chmod(path, 0775)
            return dirname + ext
        except OSError, e:
            if e.errno == errno.EEXIST:
                ext = '.' + str(i)
                continue  # try again
            raise
    raise Exception("Could not create a unique job directory")
