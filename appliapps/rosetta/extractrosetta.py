#!/usr/bin/env python
from applicake.app import WrappedApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class ExtractRosetta(WrappedApp):
    """
    Extract rosetta dataset tgz to flat folder WORKDIR
    validate implement not needed.
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('DSSOUT', 'Dssout to know which tgz to use')
        ]

    def prepare_run(self, log, info):

        info['ROSETTA_EXTRACTDIR'] = info[Keys.WORKDIR]
        archivepath = None
        for dssout in info['DSSOUT']:
            if dssout.endswith('tgz'):
                archivepath = dssout
        #goto WD extract tar, junk subdirectory
        command = "tar -C %s -vxf %s --transform 's,.*/,,' " % (info[Keys.WORKDIR], archivepath)
        return info, command


if __name__ == "__main__":
    ExtractRosetta.main()