#!/usr/bin/env python
import os
import shutil

from applicake.app import BasicApp
from applicake.apputils import dropbox
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys,KeyHelp


class Copy2SequestDropbox(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.WORKDIR,KeyHelp.WORKDIR)
        ]

    def run(self, log, info):
        info['WORKFLOW'] = dropbox.extendWorkflowID(info['WORKFLOW'])
        info['DROPBOXSTAGE'] = dropbox.make_stagebox(log, info)

        keys = [Keys.PEPXML, 'PEPCSV']
        dropbox.keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])

        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'], filename)
        shutil.copy(info['PROTXML'], filepath)

        #search.properties requires some specific fields
        info['DBASENAME'] = os.path.splitext(os.path.split(info['DBASE'])[1])[0]
        info['PARENT-DATA-SET-CODES'] = info[Keys.DATASET_CODE]

        path = os.path.join(info['DROPBOXSTAGE'], 'search.properties')
        IniInfoHandler().write(info, path)

        info['DROPBOXSTAGE'] = dropbox.move_stage_to_dropbox(log, info['DROPBOXSTAGE'], info['DROPBOX'], keepCopy=True)

        return info

if __name__ == "__main__":
    Copy2SequestDropbox.main()