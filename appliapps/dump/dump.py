#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import dirs
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import KeyHelp, Keys
from applicake.apputils import validation

class Dump(WrappedApp):
    def add_args(self):
        return [
            Argument(Keys.MZXML, KeyHelp.MZXML),
            Argument("WINDOWTYPE","window type"),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR)
        ]

    def prepare_run(self, log, info):
        info = dirs.create_workdir(log, info)

        log.info("WindowType = "+info['WINDOWTYPE'])
        basename = os.path.splitext(os.path.basename(info['MZXML']))[0]
        basename = os.path.join(info[Keys.WORKDIR], basename)
        info['DUMP_MZXML'] = [ basename + ".1.mzXML", basename + ".2.mzXML", basename + ".3.mzXML"]

        command = "dump %s %s" % (info["MZXML"], info[Keys.WORKDIR])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        for f in info['DUMP_MZXML']:
            validation.check_file(log, f)
        validation.check_exitcode(log, exit_code)
        return info

#use this class as executable
if __name__ == "__main__":
    Dump.main()
