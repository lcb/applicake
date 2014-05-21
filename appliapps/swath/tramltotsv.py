#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class ConvertTramlToTsv(WrappedApp):
    """
    phl1: 1.7G => 9min 12G => 256MB
    phl2: 2GB => 12min 14G => 560MB
    set pub.1h 15G RAM
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.DATASET_CODE, KeyHelp.DATASET_CODE),
            Argument('TRAML', 'traml'),
        ]

    def prepare_run(self, log, info):
        info['TRAML_CSV'] = os.path.join(info[Keys.WORKDIR], os.path.basename(info['TRAML']) + ".csv")

        command = 'ConvertTraMLToTSV -no_progress -in %s -out %s' % (info['TRAML'], info['TRAML_CSV'])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log,exit_code)
        validation.check_file(log,info['TRAML_CSV'])
        return info

if __name__ == "__main__":
    ConvertTramlToTsv.main()
