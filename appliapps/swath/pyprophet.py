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
        'MPR_LDA_PATH': "apply_scorer",
        'MPR_WT_PATH': "apply_weights",
        'MPR_FRACT': "xeval.fraction",
        'MPR_SSL_IF': "semi_supervised_learner.initial_fdr",
        'MPR_SSL_IL': 'semi_supervised_learner.initial_lambda',
        'MPR_SSL_TF': 'semi_supervised_learner.iteration_fdr',
        'MPR_SSL_TL': 'semi_supervised_learner.iteration_lambda',
        'MPR_SSL_NI': 'semi_supervised_learner.num_iter',
        "MPR_QVALITY_ENABLE": "qvality.enable",
        "MPR_QVALITY_EPSILONCROSSVALIDATION": "qvality.epsilon-cross-validation",
        "MPR_QVALITY_EPSILONSTEP": "qvality.epsilon-step",
        "MPR_QVALITY_GENERALIZED": "qvality.generalized",
        "MPR_QVALITY_NUMBEROFBINS": "qvality.number-of-bins",
        "MPR_QVALITY_QVALUE": "qvality.q-value",
        "MPR_MS1_SCORING_ENABLE": "ms1_scoring.enable",
        "MPR_MS1_FINAL_STATISTICS_EMP_P": "ms1.final_statistics.emp_p",
        "MPR_MS2_SCORING_ENABLE": "ms2_scoring.enable",
        "MPR_MS2_FINAL_STATISTICS_EMP_P": "ms2.final_statistics.emp_p",
        "MPR_MS2_SCORING_DETECTION_FDR_MS1": "ms2_scoring.detection_fdr_ms1",
        "MPR_UIS_SCORING_ENABLE": "uis_scoring.enable",
        "MPR_UIS_FINAL_STATISTICS_EMP_P": "uis.final_statistics.emp_p",
        "MPR_UIS_SCORING_DETECTION_FDR_MS1": "uis_scoring.detection_fdr_ms1",
        "MPR_UIS_SCORING_DETECTION_FDR_MS2": "uis_scoring.detection_fdr_ms2",
        "MPR_UIS_SCORING_DISABLE_H0": "uis_scoring.disable_h0",
        "MPR_UIS_SCORING_IDENTIFICATION_FDR": "uis_scoring.identification_fdr",
        "MPR_UIS_SCORING_IDENTIFICATION_PROBABILITY": "uis_scoring.identification_probability",
        "MPR_UIS_SCORING_ISOTOPE_OVERLAP_THRESHOLD": "uis_scoring.isotope_overlap_threshold",
    }

    def add_args(self):
        ret = [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('FEATURETSV', 'input openswathfeaturetsv'),

            Argument('MPR_MAINVAR', "main mprophet var"),
            Argument('MPR_VARS', "side mprophet vars"),
            Argument('MPR_MAYU', "true to export mayu")
        ]
        for k, v in self.opts.iteritems():
            ret.append(Argument(k, v))
        return ret

    def prepare_run(self, log, info):
        if info['MPR_MAINVAR'] in info['MPR_VARS']:
            raise RuntimeError("Mainvar [%s] occurs duplicated in vars!" % info['MPR_MAINVAR'])

        # check if vars exist in input and have values
        with open(info['FEATURETSV']) as f:
            hdr = f.readline().split("\t")
            dta = f.readline().split("\t")
        vars_to_really_use = set()
        for var in info['MPR_VARS'].split():
            if not var in "".join(hdr):
                log.warn("Requested var [%s] not found in input, thus not used for scoring" % var)
            else:
                idx = [idx for idx, col in enumerate(hdr) if var in col][0]
                if dta[idx] == "":
                    log.warn("Requested var [%s] has no values, thus ignored in scoring" % var)
                else:
                    vars_to_really_use.add(var)
                    log.debug("Requested var [%s] will be used for scoring" % var)
        info['MPR_VARS'] = " ".join(vars_to_really_use)
        # the same for mainvar but with raise
        mainvar = info['MPR_MAINVAR']
        if not mainvar in "".join(hdr):
            raise RuntimeError("Mainvar [%s] not found in input!" % mainvar)
        if dta[[idx for idx, col in enumerate(hdr) if mainvar in col][0]] == "":
            raise RuntimeError("Requested mainvar [%s] has no values!" % mainvar)
        else:
            log.debug("Requested mainvar [%s] will be used for scoring" % mainvar)

        flags = ''
        for k, v in self.opts.iteritems():
            if info.get(k, "") != "":
                flags += " --%s=%s" % (v, info[k])

        if info.get("MPR_MAYU", "") == "True":
            flags += " --export.mayu"

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
