#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class InterProphet(WrappedApp):
    """
    Wrapper for the TPP-tool InterProphetParser.
    """

    def add_args(self):
        return [
            Argument("TPPDIR",  KeyHelp.EXECDIR, default=''),
            Argument("IPROPHET_EXE", KeyHelp.EXECUTABLE, default='InterProphetParser'),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.PEPXML, KeyHelp.PEPXML),
            Argument('IPROPHET_ARGS', 'Arguments for InterProphetParser', default='MINPROB=0'),
        ]

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]
        result = os.path.join(wd, 'iprophet.pep.xml')
        if not isinstance(info[Keys.PEPXML], list):
            info[Keys.PEPXML] = [info[Keys.PEPXML]]

        command = '{exe} {arg} {pepxml} {result}'.format(exe = os.path.join(info['TPPDIR'],info['IPROPHET_EXE'])
                                                         , arg=info['IPROPHET_ARGS'],pepxml= ' '.join( info[Keys.PEPXML] ),
                                        result = result)
        info[Keys.PEPXML] = result
        return info, command


    def validate_run(self, log, info, exit_code, stdout):
        if exit_code == -8:
            raise RuntimeError("iProphet failed most probably because too few peptides were found in the search before")
        for line in stdout.splitlines():
            if 'fin: error opening' in line:
                raise RuntimeError("Could not read the input file " + line)

        validation.check_exitcode(log, exit_code)
        validation.check_xml(log, info[Keys.PEPXML])
        return info


if __name__ == "__main__":
    InterProphet.main()