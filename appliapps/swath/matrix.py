#!/usr/bin/env python
import os

import yaml

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class WriteMatrix(WrappedApp):
    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument("ALIGNMENT_TSV", ""),
            Argument("REQUANT_TSV", ""),
            Argument("ALIGNMENT_YAML", ""),
            Argument('MATRIX_FORMAT', '', default="xlsx"),
            Argument('DO_CHROMML_REQUANT', 'to skip set to false'),
        ]

    def prepare_run(self, log, info):
        if info.get('DO_CHROMML_REQUANT', "") == "false":
            intsv = info['ALIGNMENT_TSV']
            requantsv = ""
            merge = os.path.join(info['WORKDIR'], "feature_alignment.tsv")
        else:
            intsv = info['ALIGNMENT_TSV']
            requantsv = info["REQUANT_TSV"]
            if not isinstance(requantsv, list):
                requantsv = [requantsv]
            merge = os.path.join(info['WORKDIR'], "feature_alignment_requant.tsv")

        info['ALIGNMENT_MATRIX'] = os.path.join(info[Keys.WORKDIR], "matrix." + info["MATRIX_FORMAT"])
        y = yaml.load(open(info['ALIGNMENT_YAML']))
        info['ALIGNER_MSCORE_THRESHOLD'] = y['AlignedSwathRuns']['Parameters']['m_score_cutoff']

        command = "awk 'NR==1 || FNR!=1' %s %s > %s && " \
                  "compute_full_matrix.py --in %s --out_matrix %s --aligner_mscore_threshold %s --output_method full" % (
                      intsv, requantsv, merge,
                      merge, info['ALIGNMENT_MATRIX'], info['ALIGNER_MSCORE_THRESHOLD']
                  )

        info['ALIGNMENT_TSV'] = merge
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['ALIGNMENT_MATRIX'])
        return info

#use this class as executable
if __name__ == "__main__":
    WriteMatrix.main()