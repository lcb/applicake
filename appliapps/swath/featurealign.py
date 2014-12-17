#!/usr/bin/env python
import glob
import os
import shutil

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class FeatureAlignment(WrappedApp):
    """
    200 sample small lib:
    with dscore cutoff and external R: 2h20m, 5G RAM
    """
    opts = {
        'ALIGNER_FDR': "fdr_cutoff",
        'ALIGNER_MAX_RT_DIFF': 'max_rt_diff',
        'ALIGNER_MAX_FDRQUAL': "max_fdr_quality",
        'ALIGNER_FRACSELECTED': 'frac_selected',
        'ALIGNER_METHOD': "method", #clustering default=best_overall
        "ALIGNER_REALIGN_METHOD": "realign_method", #RTalign default=splineR_external

        'ALIGNER_TARGETFDR': 'target_fdr',
    }

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('MPROPHET_TSV', ''),
            Argument('ALIGNER_METHOD', ''),
            Argument("ALIGNER_REALIGNMETHOD", ""),
            Argument('ALIGNER_FRACSELECTED', ''),
            Argument('ALIGNER_MAX_RT_DIFF', ''),
            Argument('ALIGNER_TARGETFDR', '', default=-1),

            Argument('ALIGNER_FDR', 'seeding m_score (FDR) cutoff , what is used as starting points'),
            Argument('ALIGNER_MAX_FDRQUAL', 'extension m_score (FDR) cutoff, what is used for realignment points'),
            Argument('ALIGNER_REALIGNRUNS', 'true=realign, false=use iRTfaster, less datapoints, but less accurate',
                     default="true")
        ]

    def prepare_run(self, log, info):
        if not isinstance(info["MPROPHET_TSV"], list):
            info["MPROPHET_TSV"] = [info["MPROPHET_TSV"]]
        info['ALIGNMENT_TSV'] = os.path.join(info[Keys.WORKDIR], "feature_alignment.tsv")
        info['ALIGNMENT_YAML'] = os.path.join(info[Keys.WORKDIR], "feature_alignment.yaml")
        tmpdir = os.environ.get('TMPDIR', info[Keys.WORKDIR]) + '/'

        flags = ''
        for k, v in self.opts.iteritems():
            if info.get(k, "") != "":
                flags += " --%s %s" % (v, info[k])

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
