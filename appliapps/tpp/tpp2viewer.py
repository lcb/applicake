#!/usr/bin/env python
import os
import shutil
import getpass

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument


class Tpp2ViewerAndMail(WrappedApp):
    def add_args(self):
        return [
            Argument('DROPBOXSTAGE', 'location of dropbox stage folder'),
            Argument("EXPERIMENT_CODE", 'experiment code created by dropbox'),
            Argument("VIEWER_BASEPATH", 'base folder for tpp2viewer', default='/IMSB/ra/%s/html/petunia'),
            Argument("RUNTPP2VIEWER", 'do run tpp2viewer'),
        ]

    def prepare_run(self, log, info):
        if info.get('RUNTPP2VIEWER', 'no') == 'no':
            command = "echo skipping tpp2viewer"
        else:
            sonaspath = info['VIEWER_BASEPATH'] % getpass.getuser()
            if not os.path.exists(sonaspath):
                os.makedirs(sonaspath)
                os.chmod(sonaspath, 0777)
                log.debug("Created petunia folder " + sonaspath)
            tgt = os.path.join(sonaspath, info['EXPERIMENT_CODE'])
            if not os.path.exists(tgt):
                shutil.copytree(info['DROPBOXSTAGE'], tgt)

            command = "cd %s && tpp2viewer3.py %s %s" % (sonaspath, info['EXPERIMENT_CODE'], info['RUNTPP2VIEWER'])

        mailtext = os.path.join(info['DROPBOXSTAGE'], "mailtext.txt")
        command += " && mail -t < %s" % mailtext
        return info, command

    def validate_run(self, log, info, run_code, stdout):
        validation.check_exitcode(log, run_code)
        return info


if __name__ == "__main__":
    Tpp2ViewerAndMail.main()