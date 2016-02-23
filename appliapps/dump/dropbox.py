#!/usr/bin/env python
import os

from applicake.app import BasicApp
from applicake.apputils import dropbox
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys, KeyHelp


class Copy2DumpDropbox(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR)
        ]

    def run(self, log, info):
        info['WORKFLOW'] = dropbox.extendWorkflowID(info.get('WORKFLOW',"wff"))
        stagebox = dropbox.make_stagebox(log, info)

        dropbox.keys_to_dropbox(log, info, ['DUMP_MZXML'], stagebox)

        dsattr = {}
        dsattr['DATASET_TYPE'] = 'PLAIN'

        path = os.path.join(stagebox, 'dataset.attributes')
        IniInfoHandler().write(dsattr, path)

        dropbox.move_stage_to_dropbox(log, stagebox, info['DROPBOX'], keepCopy=False)

        return info

if __name__ == "__main__":
    Copy2DumpDropbox.main()