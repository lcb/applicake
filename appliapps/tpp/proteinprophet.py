#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class ProteinProphetFDR(WrappedApp):
    """
    Wrapper for TPP-tool ProteinProphet.
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE),
            Argument(Keys.PEPXML,KeyHelp.PEPXML),
            Argument('PEPTIDEFDR', 'Peptide FDR cutoff')
        ]

    def getiProbability(self, log, info):
        minprob = ''

        for line in open(info[Keys.PEPXML]):
            if line.startswith('<error_point error="%s' % info['PEPTIDEFDR']):
                minprob = line.split(" ")[2].split("=")[1].replace('"', '')
                break

        if minprob != '':
            log.info("Found minprob/iprobability %s for PEPTIDEFDR %s" % (minprob, info['PEPTIDEFDR']))
        else:
            raise Exception("error point for PEPTIDEFDR %s not found" % info['PEPTIDEFDR'])
        return minprob

    def prepare_run(self, log, info):
        if isinstance(info[Keys.PEPXML],list):
            raise RuntimeError("This ProteinProphet only takes one iProphet inputfile!")

        info['IPROBABILITY'] = self.getiProbability(log, info)
        info['PROTEINPROPHET'] = 'IPROPHET MINPROB%s' % info['IPROBABILITY']
        wd = info[Keys.WORKDIR]
        info['PROTXML'] = os.path.join(wd, 'ProteinProphet.prot.xml')
        exe = info.get(Keys.EXECUTABLE, 'ProteinProphet')
        command = '%s %s %s %s' % (exe, info[Keys.PEPXML], info['PROTXML'], info['PROTEINPROPHET'])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)

        for msg in ['did not find any InterProphet results in input data!',
                    'no data - quitting',
                    'WARNING: No database referenced']:
            if msg in stdout:
                raise RuntimeError('ProteinProphet error [%s]' % msg)

        validation.check_xml(log, info[Keys.PEPXML])
        return info

if __name__ == "__main__":
    ProteinProphetFDR.main()