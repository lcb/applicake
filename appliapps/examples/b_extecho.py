#!/usr/bin/env python
from applicake.app import WrappedApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class ExternalEcho(WrappedApp):
    """
    A most simple example for a WrappedApp
    prints COMMENT to stdout using '/bin/echo'

    Note: validate run not overwritten here because default is OK
    """

    def add_args(self):
        return [
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE, default="echo"),
            Argument("COMMENT", "String to be displayed", default="default comment")
        ]

    def prepare_run(self, log, info):
        exe = info["EXECUTABLE"]
        comment = info["COMMENT"]
        command = "%s %s" % (exe, comment)
        log.debug("Executable is " + exe)
        log.info("Comment is " + comment)
        return info, command

#use this class as executable
if __name__ == "__main__":
    ExternalEcho.main()