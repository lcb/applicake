#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class SpectrastIrtCalibrator(WrappedApp):
    """
    Wrapper for spectrast2spectrast_irt.py
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE),
            Argument('SPLIB', 'Input spectrast library in .splib format'),
            Argument('RSQ_THRESHOLD', 'specify r-squared threshold to accept linear regression'),
            Argument('RTKIT', 'RT kit'),
            Argument('APPLYCAUVENET', 'should Chavenets criterion be used to exclude outliers?'),
            Argument('PRECURSORLEVEL', 'should precursors instead of peptides be used for grouping?'),
            Argument('SPECTRALEVEL',
                     'do not merge or group any peptides or precursors (use raw spectra)')
        ]

    def prepare_run(self, log, info):
        exe = info.get(Keys.EXECUTABLE, 'spectrast2spectrast_irt.py')
        input_splib = info['SPLIB']
        info['SPLIB'] = os.path.join(info[Keys.WORKDIR], 'RawRTcalib.splib')

        options = ''
        if info.get('RTKIT', "") != "":
            options += " -k " + info['RTKIT'].replace(";", ",")
        if info.get('APPLYCHAUVENET', "") == "True":
            options += " --applychauvenet"
        if info.get('PRECURSORLEVEL', "") == "True":
            options += " --precursorlevel"
        if info.get('SPECTRALEVEL', "") == "True":
            options += " --spectralevel"

        command = '%s -i %s -o %s --rsq_threshold %s %s' % (
            exe, input_splib, info['SPLIB'], info['RSQ_THRESHOLD'], options)
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        for line in stdout.splitlines():
            if 'below the threshold of' in line:
                raise RuntimeError("iRT calibration failed: " + line.strip())
        validation.check_exitcode(log, exit_code)
        validation.check_file(log,info['SPLIB'])
        validation.check_file(log,info['SPLIB'].replace('.splib','.pepidx'))
        return info

if __name__ == "__main__":
    SpectrastIrtCalibrator.main()