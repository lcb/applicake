"""
Created on Jun 19, 2012

@author: quandtan
"""

import os
import shutil
import subprocess

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication
from applicake.utils.fileutils import FileUtils
from applicake.framework.informationhandler import IniInformationHandler
from applicake.utils.dictutils import DictUtils


class Copy2Dropbox(IApplication):
    """
    Minimal working example for copy to generic dropbox. Registers dataset in openBIS by
    * copying resultfiles to stagebox
    * creating required dataset.attributes
    * move stage to dropbox
    """

    def main(self, info, log):
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        stagebox = self._make_stagebox(log, info)

        self._keys_to_dropbox(log, info, ['RESULTFILES'], stagebox)

        dsattr = {}
        dsattr['SPACE'] = info['SPACE']
        dsattr['DATASET_TYPE'] = info['DATASET_TYPE']
        dsattr[Keys.OUTPUT] = os.path.join(stagebox, 'dataset.attributes')
        IniInformationHandler().write_info(dsattr, log)

        self._move_stage_to_dropbox(stagebox, info['DROPBOX'], keepCopy=False)
        return 0, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, "WORKDIR", "")

        #TODO: simplify "wholeinfo" apps
        args_handler.add_app_args(log, Keys.INPUT, 're-read input to access whole info')
        args_handler.add_app_args(log, Keys.BASEDIR, 'get basedir if set or modified by runner')
        args_handler.add_app_args(log, Keys.JOB_IDX, 'get jobidx if set or modified by runner')
        args_handler.add_app_args(log, Keys.STORAGE, 'get storage if set or modified by runner')
        args_handler.add_app_args(log, Keys.LOG_LEVEL, 'get loglevel if set or modified by runner')
        return args_handler

    ###########################################
    ### Utility methods for derived classes ###
    ###########################################  

    def _get_experiment_code(self, info):
        #caveat: fails if no job_idx defined.
        ecode = 'E' + info[Keys.JOB_IDX]
        if info.has_key(Keys.PARAM_IDX) and info[Keys.PARAM_IDX] != "0":
            ecode = '%s_%s' % (ecode, info[Keys.PARAM_IDX])
        if info.has_key(Keys.FILE_IDX) and info[Keys.FILE_IDX] != "0":
            ecode = '%s-%s' % (ecode, info[Keys.FILE_IDX])
        return ecode

    def _make_stagebox(self, log, info):
        dirname = ""
        if 'SPACE' in info:
            dirname += info['SPACE'] + "+"
        if 'PROJECT' in info:
            dirname += info['PROJECT'] + "+"
        dirname += self._get_experiment_code(info)
        dirname = os.path.join(info[Keys.WORKDIR], dirname)
        log.info("stagebox is " + dirname)
        FileUtils.makedirs_safe(log, dirname, clean=True)
        return dirname

    def _keys_to_dropbox(self, log, info, keys, tgt):
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
                    if FileUtils.is_valid_file(log, file):
                        log.debug('File [%s] already exists, ignore' % file)
                    else:
                        raise Exception('Stop program because could not copy [%s] to [%s]' % (file, tgt))


    def _move_stage_to_dropbox(self, stage, dropbox, keepCopy=False):
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

        shutil.move(stage, dropbox)
        return newstage

    def _extendWorkflowID(self, wfstring):
        applivers = subprocess.check_output("awk 'NR==4' /cluster/apps/guse/stable/applicake/trunk/.svn/entries",
                                            shell=True).strip()
        imsbtoolvers = subprocess.check_output("printenv LOADEDMODULES| grep -o 'imsbtools/[^:]*' | tail -1",
                                               shell=True).strip()
        return wfstring + " " + imsbtoolvers + " applicake@" + applivers
