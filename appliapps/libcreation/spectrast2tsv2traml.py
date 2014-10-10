#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class Spectrast2TSV2traML(WrappedApp):
    """
    Wrapper for the famous spectrast2traml.sh script
    """

    def add_args(self):
        return [
            Argument('SPLIB', 'Spectrast library in .splib format'),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),

            Argument('CONSENSUS_TYPE', 'consensus type cAC cAB'),

            Argument('TSV_MASS_LIMITS', 'Lower and Upper mass limits.'),
            Argument('TSV_ION_LIMITS', 'Min and Max number of reported ions per peptide/z'),
            Argument('TSV_PRECISION', 'Maximum error allowed at the annotation of a fragment ion'),
            Argument('TSV_REMOVE_DUPLICATES', 'Remove duplicate masses from labeling'),
            Argument('TSV_EXACT', 'Use exact mass.'),
            Argument('TSV_GAIN',
                     'List of allowed fragment mass modifications. Useful for phosphorilation.'),
            Argument('TSV_CHARGE', 'Fragment ion charge states allowed.'),
            Argument('TSV_SERIES', 'List of ion series to be used'),
            Argument('SWATH_WINDOW_FILE', 'swath window file')
        ]

    def prepare_run(self, log, info):

        info['TSV'] = os.path.join(info[Keys.WORKDIR], 'spectrast2tsv.tsv')
        info['TRAML'] = os.path.join(info[Keys.WORKDIR], 'ConvertTSVToTraML.TraML')

        tsvopts = '-k openswath '
        tsvopts += ' -l ' + info['TSV_MASS_LIMITS'].replace("-", ",")
        try:
           _, _ = info['TSV_ION_LIMITS'].split("-")
        except:
            raise RuntimeError("Ions per peptide [%s] not in format n-m!" % info['TSV_ION_LIMITS'])
        mini, maxi = info['TSV_ION_LIMITS'].split("-")
        tsvopts += ' -o %s -n %s ' % (mini, maxi)
        tsvopts += ' -p ' + info['TSV_PRECISION']

        if info.get('TSV_REMOVE_DUPLICATES', "") == "True":
            tsvopts += ' -d'

        if info.get('TSV_EXACT', "") == "True":
            tsvopts += ' -e'

        if info.get('TSV_CHARGE', "") != "":
            tsvopts += ' -x ' + info['TSV_CHARGE'].replace(";", ",")

        if info.get('SWATH_WINDOW_FILE', "") != "":
            tsvopts += ' -w ' + info['SWATH_WINDOW_FILE']

        if info.get('TSV_GAIN', "") != "":
            tsvopts += ' -g ' + info['TSV_GAIN'].replace(";", ",")

        if info.get('TSV_SERIES', "") != "":
            tsvopts += ' -s ' + info['TSV_SERIES'].replace(";", ",")

        command = 'spectrast2tsv.py %s -a %s %s && ' \
                  'tsv2traml.sh %s %s' % (
                      tsvopts, info['TSV'], info['SPLIB'],
                      info['TSV'], info['TRAML'])

        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_stdout(log,stdout)
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['SPLIB'])
        validation.check_file(log, info['TSV'])
        validation.check_xml(log, info['TRAML'])
        return info

if __name__ == "__main__":
    Spectrast2TSV2traML.main()