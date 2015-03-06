#!/usr/bin/env python
import os
import getpass
import time

from configobj import ConfigObj

from applicake.app import BasicApp
from applicake.apputils import dropbox
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys, KeyHelp


class Copy2LibcreateDropbox(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR)
        ]

    def run(self, log, info):
        info['WORKFLOW'] = dropbox.extendWorkflowID(info['WORKFLOW'])
        info['DROPBOXSTAGE'] = stagebox = dropbox.make_stagebox(log, info)

        info['PEPIDX'] = info['SPLIB'].replace(".splib", ".pepidx")
        dropbox.keys_to_dropbox(log, info, ['SPLIB', 'PEPIDX', 'TSV', 'TRAML'], stagebox)

        dsattr = {}
        dsattr['SPACE'] = 'PERSONAL_DB'
        dsattr['PROJECT'] = 'TRAML'
        dsattr['EXPERIMENT'] = getpass.getuser().upper()
        dsattr['EXPERIMENT_TYPE'] = "PLAIN"
        dsattr['DATASET_TYPE'] = 'TRAML_DB'
        dsattr['PARENT_DATASETS'] = os.path.basename(os.path.dirname(info[Keys.PEPXML]))

        path = os.path.join(stagebox, 'dataset.attributes')
        IniInfoHandler().write(dsattr, path)

        dsprop = {}
        dsprop['VERSION'] = time.strftime("%Y%m%d%H%M%S")
        dsprop['NAME'] = info.get('COMMENT', "unnamed")
        dsprop['DESCRIPTION'] = info.get('DESCRIPTION', "undescribed")
        dsprop['WORKFLOW'] = info['WORKFLOW']
        dsprop['HASSPLIB'] = "true"

        for key in ["FDR", "MS_TYPE", "RUNRT", "RTKIT",
                    "TSV_MASS_LIMITS", "TSV_ION_LIMITS", "TSV_PRECISION", "TSV_CHARGE", "TSV_REMOVE_DUPLICATES",
                    "TSV_EXACT", "TSV_GAIN", "TSV_SERIES", "CONSENSUS_TYPE"]:
            dsprop[key] = info[key]

        #cannot use IniInfoHandlerHere because it writes NAME
        config = ConfigObj(dsprop)
        config.filename = os.path.join(stagebox, 'dataset.properties')
        config.write()

        dropbox.move_stage_to_dropbox(log, stagebox, info['DROPBOX'], keepCopy=False)

        return info


if __name__ == "__main__":
    Copy2LibcreateDropbox.main()