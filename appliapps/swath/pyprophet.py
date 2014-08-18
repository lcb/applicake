#!/usr/bin/env python
import os

from applicake.apputils import validation

from applicake.app import WrappedApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class PyProphet(WrappedApp):
    """
    ups1 1.7GB file: 4min 4G RAM
    phl2 3.7GB file: 7min 6600M RAM
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.THREADS, KeyHelp.THREADS, default='1'),
            Argument('FEATURETSV', 'input openswathfeaturetsv'),
            Argument('MPR_NUM_XVAL', 'num cross validations'),
            Argument('MPR_MAINVAR', 'mProphet main score'),
            Argument('MPR_VARS', 'mProphet other scores'),
            Argument('MPR_LDA_PATH', 'mProphet use existing LDA model')
        ]

    def prepare_run(self, log, info):
        classify = ''
        if info.get('MPR_LDA_PATH', "") != "":
            classify = " --apply=" + info['MPR_LDA_PATH']
        command = 'mProphetScoreSelector.sh %s %s %s && ' \
                  'pyprophet --ignore.invalid_score_columns --target.dir=%s --xeval.num_iter=%s %s %s' % (
                      info['FEATURETSV'], info['MPR_MAINVAR'], info['MPR_VARS'],
                      info[Keys.WORKDIR], info['MPR_NUM_XVAL'], classify, info['FEATURETSV'])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_stdout(log,stdout)
        validation.check_exitcode(log, exit_code)

        base = os.path.join(info[Keys.WORKDIR], os.path.splitext(os.path.basename(info['FEATURETSV']))[0])
        info['MPROPHET_TSV'] = base + "_with_dscore.csv"
        validation.check_file(log, info['MPROPHET_TSV'])

        prophet_stats = []
        for end in ["_full_stat.csv", "_scorer.bin", "_report.pdf", "_dscores_top_target_peaks.txt",
                    "_dscores_top_decoy_peaks.txt"]:
            f = base + end
            if os.path.exists(f):
                prophet_stats.append(f)

        if prophet_stats:
            info['MPROPHET_STATS'] = prophet_stats
        return info


if __name__ == "__main__":
    PyProphet.main()