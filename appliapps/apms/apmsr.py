#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class ApmsR(WrappedApp):
    def add_args(self):
        return [
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE, default="alfq.R"),
            Argument('DBASE', 'fasta dbase'),
            Argument('ASSOC_FILE', 'assoc table'),
            Argument('PEPCSV', 'pepxml2csv'),
            Argument('IPROBABILITY', 'iprob', default='0.9'),
            Argument('COMPPASS_CONFIDENCE', 'confidence', default='0.95'),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
        ]

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]
        csv = os.path.join(wd, 'pepxml2csv.csv')
        os.symlink(info['PEPCSV'], csv)
        assoc = os.path.join(wd, 'assoc.txt')
        os.symlink(info['ASSOC_FILE'], assoc)
        fasta = os.path.join(wd, 'fasta.fasta')
        os.symlink(info['DBASE'], fasta)

        info['APMS_OUT'] = []
        for i in ['comppass', 'gfpratio', 'merged']:
            info['APMS_OUT'].append(os.path.join(wd, 'iaLFQ_%s.csv' % i))
        command = 'cd %s && %s pepxml2csv.csv assoc.txt fasta.fasta %s %s' % (wd, info[Keys.EXECUTABLE],
                                                                              info['IPROBABILITY'],
                                                                              info['COMPPASS_CONFIDENCE'])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)

        for i in info['APMS_OUT']:
            validation.check_file(log, i)

        return info


if __name__ == "__main__":
    ApmsR.main()