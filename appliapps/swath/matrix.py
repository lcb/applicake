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
            Argument('MATRIX_FORMAT', '', default="xlsx")
        ]

    def prepare_run(self, log, info):
        if not isinstance(info["REQUANT_TSV"], list):
            info["REQUANT_TSV"] = [info["REQUANT_TSV"]]

        y = yaml.load(open(info['ALIGNMENT_YAML']))
        info['ALIGNER_MSCORE_THRESHOLD'] = y['AlignedSwathRuns']['Parameters']['m_score_cutoff']

        info['ALIGNMENT_MATRIX'] = os.path.join(info[Keys.WORKDIR], "matrix." + info["MATRIX_FORMAT"])

        tmpdir = os.environ.get('TMPDIR',info[Keys.WORKDIR])
        merge = os.path.join(tmpdir,"merge")

        command = "awk 'NR==1 || FNR!=1' %s %s > %s && " \
                  "compute_full_matrix.py --in %s --out_matrix %s --aligner_mscore_threshold %s --output_method full" % (
                      info['ALIGNMENT_TSV'], " ".join(info['REQUANT_TSV']), merge,
                      merge, info['ALIGNMENT_MATRIX'], info['ALIGNER_MSCORE_THRESHOLD']
                  )
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['ALIGNMENT_MATRIX'])
        return info

#use this class as executable
if __name__ == "__main__":
    WriteMatrix.main()