#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: loblum
"""
import os
import shutil
import getpass

from applicake.framework.interfaces import IWrapper


class Tpp2Viewer(IWrapper):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, 'DROPBOXSTAGE', 'copy of dropbox folder')
        args_handler.add_app_args(log, "EXPERIMENT_CODE", '')
        args_handler.add_app_args(log, "BASEPATH", '',default='/IMSB/ra/%s/html/petunia')
        args_handler.add_app_args(log, "RUNTPP2VIEWER", '')

        return args_handler

    def prepare_run(self, info, log):
        if not 'RUNTPP2VIEWER' in info or info['RUNTPP2VIEWER'] == 'no':
            command = "echo skipping tpp2viewer"
        else:
            sonaspath = info['BASEPATH'] % getpass.getuser()
            if not os.path.exists(sonaspath):
                os.makedirs(sonaspath)
                os.chmod(sonaspath,0777)
                log.debug("Created petunia folder " + sonaspath)
            tgt = os.path.join(sonaspath, info['EXPERIMENT_CODE'])
            if not os.path.exists(tgt):
                shutil.copytree(info['DROPBOXSTAGE'], tgt)

            command = "cd %s && tpp2viewer3.py %s %s" % (sonaspath, info['EXPERIMENT_CODE'], info['RUNTPP2VIEWER'])

        mailtext = os.path.join(info['DROPBOXSTAGE'], "mailtext.txt")
        command += " && mail -t < %s" % mailtext
        return command, info

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info
        return 0, info
