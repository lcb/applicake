"""
Created on Oct 24, 2012

ups1 1.7GB file: 4min 4G RAM
phl2 3.7GB file: 7min 6600M RAM

@author: lorenz
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils


class pyProphet(IWrapper):
    def prepare_run(self, info, log):
        classify = ''
        if 'MPR_LDA_PATH' in info and info['MPR_LDA_PATH'] != "":
            classify = " --apply=" + info['MPR_LDA_PATH']
        command = 'mProphetScoreSelector.sh %s %s %s && pyprophet --ignore.invalid_score_columns --target.dir=%s --xeval.num_iter=%s %s %s' % (
            info['FEATURETSV'], info['MPR_MAINVAR'], info['MPR_VARS'],
            info['WORKDIR'], info['MPR_NUM_XVAL'], classify, info['FEATURETSV'])
        return command, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, 'WORKDIR', 'wd')
        args_handler.add_app_args(log, 'THREADS', 'number of threads', default='1')
        args_handler.add_app_args(log, 'FEATURETSV', 'featuretsv')
        args_handler.add_app_args(log, 'MPR_NUM_XVAL', 'num cross validations')
        args_handler.add_app_args(log, 'MPR_MAINVAR', 'mProphet main score')
        args_handler.add_app_args(log, 'MPR_VARS', 'mProphet other scores')
        args_handler.add_app_args(log, 'MPR_LDA_PATH', 'mProphet use existing LDA model')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):

        if 'MemoryError' in out_stream.read():
            log.error('Ran out of memory!')
            return 1,info

        out_stream.seek(0)
        for line in out_stream.readlines():
            if line.startswith("Exception:"):
                log.error(line)
                return 1,info

        base = os.path.join(info[Keys.WORKDIR], os.path.splitext(os.path.basename(info['FEATURETSV']))[0])
        resultfile = base + "_with_dscore.csv"
        if not FileUtils.is_valid_file(log, resultfile):
            log.critical('%s is not valid', resultfile)
            return 1, info
        else:
            info['MPROPHET_TSV'] = resultfile

        info['MPROPHET_STATS'] = []
        for end in ["_full_stat.csv", "_scorer.bin", "_report.pdf",
                    "_dscores_top_target_peaks.txt", "_dscores_top_decoy_peaks.txt"]:
            f = base + end
            if not FileUtils.is_valid_file(log, f):
                log.debug("Ignoring above message, not adding")
            else:
                log.debug("Adding pyprophet stat file " + f)
                info['MPROPHET_STATS'].append(f)

        if not info['MPROPHET_STATS']:
            del info['MPROPHET_STATS']
        return run_code, info
