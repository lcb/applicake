#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys


class TxtlibNoiRT(WrappedApp):
    """
    Filter out iRT peptides from RT calibrated spectral library
    """

    def add_args(self):
        return [
            Argument('SPLIB', 'Spectrast library in .splib format'),
            Argument(Keys.WORKDIR, 'Directory to store files')
        ]

    def prepare_run(self, log, info):
        orig_splib = info['SPLIB']
        basename = os.path.join(info[Keys.WORKDIR], 'TxtlibNoiRT')
        command = "spectrast -c_BIN! -cf'Protein!~iRT' -cN%s %s" % (basename, orig_splib)
        info['SPLIB'] = basename + '.splib'
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['SPLIB'])
        return info


if __name__ == "__main__":
    TxtlibNoiRT.main()