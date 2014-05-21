#!/usr/bin/env python
import os

from applicake.app import BasicApp
from applicake.apputils import dropbox
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys, KeyHelp


class Copy2RosettaDropbox(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR)
        ]

    def run(self, log, info):
        info['WORKFLOW'] = dropbox.extendWorkflowID(info['WORKFLOW'])
        stagebox = dropbox.make_stagebox(log, info)

        dropbox.keys_to_dropbox(log, info, ['ROSETTA_COMPRESSEDOUT'], stagebox)

        dsattr = {}
        dsattr['SPACE'] = info['SPACE']
        dsattr['PROJECT'] = info['PROJECT']
        dsattr['EXPERIMENT'] = info['OUTEXPERIMENT']
        dsattr['DATASET_TYPE'] = 'ROSETTA_OUTFILE'

        path = os.path.join(stagebox, 'dataset.attributes')
        IniInfoHandler().write(dsattr, path)

        dsprop = {}
        for key in ['SEQ', 'COMMENT', 'ROSETTA_VERSION', 'RUN__PROTOCOL', 'RUN__SHUFFLE', 'INFRASTRUCTURE', 'N_MODELS',
                    'DATABASE', 'IN__FILE__ALIGNMENT', 'CM__ALN_FORMAT', 'FRAG3', 'FRAG9', 'IN__FILE__FASTA',
                    'IN__FILE__FULLATOM',
                    'IN__FILE__PSIPRED_SS2', 'IN__DETECT_DISULF', 'IN__FILE__TEMPLATE_PDB', 'LOOPS__FRAG_SIZES',
                    'LOOPS__FRAG_FILES',
                    'IDEALIZE_AFTER_LOOP_CLOSE', 'LOOPS__EXTENDED', 'LOOPS__BUILD_INITIAL', 'LOOPS__REMODEL',
                    'LOOPS__RELAX',
                    'RANDOM_GROW_LOOPS_BY', 'SELECT_BEST_LOOP_FROM', 'RELAX__FAST', 'RELAX__DEFAULT_REPEATS',
                    'SILENT_DECOYTIME',
                    'FAIL_ON_BAD_HBOND', 'BGDT', 'EVALUATION__GDTMM', 'OUT__FILE__SILENT_STRUCT_TYPE']:
            dsprop[key] = info[key]

        path = os.path.join(stagebox, 'dataset.properties')
        IniInfoHandler().write(dsprop, path)

        dropbox.move_stage_to_dropbox(log, stagebox, info['DROPBOX'], keepCopy=False)

        return info


if __name__ == "__main__":
    Copy2RosettaDropbox.main()