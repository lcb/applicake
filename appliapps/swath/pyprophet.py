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
    opts = {
        'MPR_DSCORE_CUTOFF': "d_score.cutoff",
        'MPR_NUM_XVAL': "xeval.num_iter",
        'MPR_FRACT': "xeval.fraction",
        'MPR_LDA_PATH': "apply_scorer",
        'MPR_WT_PATH': "apply_weights",
        'MPR_SSL_IF': "semi_supervised_learner.initial_fdr",
        'MPR_SSL_IL': 'semi_supervised_learner.initial_lambda',
        'MPR_SSL_TF': 'semi_supervised_learner.iteration_fdr',
        'MPR_SSL_TL': 'semi_supervised_learner.iteration_lambda',
        'MPR_SSL_NI': 'semi_supervised_learner.num_iter',
        'MPR_MAYU': "export.mayu",
    }

    def add_args(self):
        ret = [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('FEATURETSV', 'input openswathfeaturetsv'),
        ]
        for k, v in self.opts.iteritems():
            ret.append(Argument(k, v))
        return ret

    def prepare_run(self, log, info):
        flags = ''
        for k, v in self.opts.iteritems():
            if info.get(k, "") != "":
                flags += " --%s=%s" % (v, info[k])

        command = 'mProphetScoreSelector.sh %s %s %s && ' \
                  'pyprophet --ignore.invalid_score_columns --target.dir=%s %s %s' % (
                      info['FEATURETSV'], info['MPR_MAINVAR'], info['MPR_VARS'],
                      info[Keys.WORKDIR], flags, info['FEATURETSV'])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_stdout(log, stdout)
        validation.check_exitcode(log, exit_code)

        base = os.path.join(info[Keys.WORKDIR], os.path.splitext(os.path.basename(info['FEATURETSV']))[0])
        info['MPROPHET_TSV'] = base + "_with_dscore_filtered.csv"
        validation.check_file(log, info['MPROPHET_TSV'])

        prophet_stats = []
        for end in ["_full_stat.csv", "_scorer.bin", "_weights.txt", "_report.pdf", "_dscores_top_target_peaks.txt",
                    "_dscores_top_decoy_peaks.txt"]:
            f = base + end
            if os.path.exists(f):
                prophet_stats.append(f)

        if prophet_stats:
            info['MPROPHET_STATS'] = prophet_stats
        return info


if __name__ == "__main__":
    PyProphet.main()