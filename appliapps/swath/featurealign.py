#!/usr/bin/env python
import glob
import os
import shutil

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class FeatureAlignment(WrappedApp):

    opts = {
        'ALIGNER_TARGETFDR': 'target_fdr',
        'ALIGNER_MAX_RT_DIFF': 'max_rt_diff',

        'ALIGNER_METHOD': "method", #clustering default=best_overall
        'ALIGNER_FDR': "fdr_cutoff",
        'ALIGNER_MAX_FDRQUAL': "max_fdr_quality",
        'ALIGNER_FRACSELECTED': 'frac_selected',
        'ALGNER_MST_USERTCORR' : 'mst:useRTCorrection',
        'ALIGNER_MST_STDEVMULT' : 'mst:Stdev_multiplier',
        'ALIGNER_ALIGNSCORE':'alignment_score',
    }

    def add_args(self):
        ret = [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('MPROPHET_TSV', 'mprophet outputfiles to use for alignment'),
            Argument('ISOTOPIC_GROUPING','featurealingn+requant: enable/disable isotopic grouping'),
            Argument("ALIGNER_REALIGN_METHOD", "realign_method")
        ]
        for k, v in self.opts.iteritems():
            ret.append(Argument(k, v))
        return ret

    def prepare_run(self, log, info):
        if not isinstance(info["MPROPHET_TSV"], list):
            info["MPROPHET_TSV"] = [info["MPROPHET_TSV"]]
            #bugfix: when only 1 sample, stdev is 0 and aligner produces no output, so override to 30s
            if "auto" in info["ALIGNER_MAX_RT_DIFF"]:
                log.warn("Set max_RT_diff to 30 seconds because auto... fails for only 1 sample")
                info["ALIGNER_MAX_RT_DIFF"] = "30"
        info['ALIGNMENT_TSV'] = os.path.join(info[Keys.WORKDIR], "feature_alignment.tsv")
        info['ALIGNMENT_YAML'] = os.path.join(info[Keys.WORKDIR], "feature_alignment.yaml")
        tmpdir = os.environ.get('TMPDIR', info[Keys.WORKDIR]) + '/'

        flags = ''
        for k, v in self.opts.iteritems():
            if info.get(k, "") != "":
                flags += " --%s %s" % (v, info[k])

        if info["ALIGNER_REALIGN_METHOD"] == "iRT":
            info["ALIGNER_REALIGN_METHOD"] = "diRT"
        #elif info["ALIGNER_REALIGN_METHOD"] == "linear":
        #    info["ALIGNER_REALIGN_METHOD"] = "linear"
        elif info["ALIGNER_REALIGN_METHOD"] == "spline":
            log.info("Changing ALIGNER_REALIGN_METHOD to splineR_external")
            info["ALIGNER_REALIGN_METHOD"] = "splineR_external"
        elif info["ALIGNER_REALIGN_METHOD"] == "lowess":
            log.info("Changing ALIGNER_REALIGN_METHOD to lowess_cython")
            info["ALIGNER_REALIGN_METHOD"] = "lowess_cython"
        else:
            log.debug("Leaving aligner realign method "+info["ALIGNER_REALIGN_METHOD"])
        flags += " --realign_method "+info["ALIGNER_REALIGN_METHOD"]

        if info['ISOTOPIC_GROUPING'] == "false":
            flags += " --disable_isotopic_grouping "

        command = "feature_alignment.py --file_format openswath --in %s --out %s " \
                  "--out_meta %s --tmpdir %s %s" % (
                      " ".join(info["MPROPHET_TSV"]), info['ALIGNMENT_TSV'],
                      info['ALIGNMENT_YAML'], tmpdir, flags)

        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_stdout(log, stdout)
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['ALIGNMENT_TSV'])
        validation.check_file(log, info['ALIGNMENT_YAML'])

        out2log = os.path.join(info[Keys.WORKDIR], "feature_alignment.out.txt")
        f = open(out2log, "w")
        f.write(stdout)
        f.close()
        info["ALIGNER_STDOUT"] = out2log
        for line in stdout.splitlines():
            if "We were able to quantify " in line:
                aligned = int(line.split()[13])
                before = int(line.split()[19])
                if aligned<before/2:
                    log.warn("Much less features after alignment than before!")


        # Move out .tr files of pyprophet to be rescue safe
        info["TRAFO_FILES"] = []
        for fil in info["MPROPHET_TSV"]:
            trfile = glob.glob(os.path.dirname(fil) + "/*.tr")
            if len(trfile) != 1:
                raise RuntimeError("More than one .tr file for " + fil)
            basename = os.path.basename(trfile[0])
            tgt = os.path.join(info['WORKDIR'], basename)
            log.debug("Moved tr file %s into WORKDIR" % basename)
            shutil.move(trfile[0], tgt)
            info["TRAFO_FILES"].append(tgt)

        return info


if __name__ == "__main__":
    FeatureAlignment.main()
