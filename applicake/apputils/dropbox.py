import os
import shutil
import subprocess
from applicake.apputils import dirs,validation

from applicake.coreutils.keys import Keys


def get_experiment_code(info):
    #caveat: fails if no job_idx defined.
    uniq_exp_code = 'E' + info[Keys.JOB_ID]
    if info.get(Keys.SUBJOBLIST, "") != "":
        for subjob in info[Keys.SUBJOBLIST]:
            uniq_exp_code += "_" + subjob.split(Keys.SUBJOBSEP)[1]

    return uniq_exp_code

def make_stagebox(log, info):
    dirname = ""
    if 'SPACE' in info:
        dirname += info['SPACE'] + "+"
    if 'PROJECT' in info:
        dirname += info['PROJECT'] + "+"
    dirname += get_experiment_code(info)
    dirname = os.path.join(info[Keys.WORKDIR], dirname)
    log.debug("stagebox is " + dirname)
    dirs.makedirs_clean(dirname)
    return dirname


def keys_to_dropbox(log, info, keys, tgt):
    if not isinstance(keys, list):
        keys = [keys]
    for key in keys:
        if not info.has_key(key):
            raise Exception('key [%s] not found in info for copying to dropbox' % key)
        if isinstance(info[key], list):
            files = info[key]
        else:
            files = [info[key]]
        for file in files:
            try:
                log.debug('Copy [%s] to [%s]' % (file, tgt))
                shutil.copy(file, tgt)
            except:
                if validation.check_file(log, file):
                    log.debug('File [%s] already exists, ignore' % file)
                else:
                    raise Exception('Could not copy [%s] to [%s]' % (file, tgt))


def move_stage_to_dropbox(log, stage, dropbox, keepCopy=False):
    #empty when moved, stage_copy when keepcopy
    newstage = ""
    if keepCopy:
        newstage = stage + '_copy'
        shutil.copytree(stage, newstage)

    #extend permissions for dropbox copy job
    os.chmod(stage, 0775)
    for dirpath, _, filenames in os.walk(stage):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            os.chmod(path, 0775)

    log.debug("Moving stage [%s] to dropbox [%s]"%(stage,dropbox))
    shutil.move(stage, dropbox)
    return newstage


def extendWorkflowID(wfstring):
    applivers = subprocess.check_output("git --git-dir=/cluster/apps/guse/stable/applicake/master/.git rev-parse --short HEAD",
                                        shell=True).strip()
    imsbtoolvers = subprocess.check_output("printenv LOADEDMODULES| grep -o 'imsbtools/[^:]*' | tail -1",
                                           shell=True).strip()
    return wfstring + " " + imsbtoolvers + " applicake@" + applivers
