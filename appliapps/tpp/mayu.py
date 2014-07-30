#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class Mayu(WrappedApp):
    """
    Wrapper for mayu
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE, default='Mayu.pl'),
            Argument(Keys.PEPXML, KeyHelp.PEPXML),
            Argument('DBASE', 'fasta database'),
            Argument('MISSEDCLEAVAGE', 'missed cleavages'),
            Argument('MAYU_MASS_RANGE','min-max peptide mass to consider'),
            Argument("MAYU_REMAMB",'mayu remove ambiguous peptides')
        ]

    def prepare_run(self, log, info):
        outbase = os.path.join(info[Keys.WORKDIR], 'mayuout')
        info['MAYUOUT'] = outbase + '_main_1.07.csv'

        minmass, maxmass = info['MAYU_MASS_RANGE'].split("-")
        remamb = ""
        if info.get('MAYU_REMAMB', "") == "True":
            remamb = "-remamb"
        command = "%s -A %s -C %s -I %s -E DECOY_ -G 0.1 -H 501 -M %s -J %s -K %s %s" % (
            info[Keys.EXECUTABLE], info[Keys.PEPXML], info['DBASE'], info['MISSEDCLEAVAGE'], outbase, minmass, maxmass,
            remamb)

        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['MAYUOUT'])
        return info


if __name__ == "__main__":
    Mayu.main()