#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils.dirs import create_workdir
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import KeyHelp, Keys


class CpApp(WrappedApp):
    """
    A more advanced example for a WrappedApp
    copies FILE to COPY using 'cp', and implements own validation routine
    """

    def add_args(self):
        return [
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE, default='cp'),
            Argument("FILE", "File to be copied"),
            Argument(Keys.WORKDIR, "folder where FILE will go into, created if not specified.")
        ]

    def prepare_run(self, log, info):
        info = create_workdir(log, info)
        info['COPY'] = os.path.join(info[Keys.WORKDIR], os.path.basename(info['FILE']))
        command = "%s %s %s" % (info['EXECUTABLE'], info["FILE"], info['COPY'])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        log.debug("Cp validation")
        #self checked
        if "No such file" in stdout:
            raise RuntimeError("Inputfile not found")

        if "Permission denied" in stdout:
            raise RuntimeError("Was not allowed to read inputfile. Need more rights")
        #validation util
        validation.check_file(log, info['COPY'])
        validation.check_exitcode(log, exit_code)
        return info

#use this class as executable
if __name__ == "__main__":
    CpApp.main()
