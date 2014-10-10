#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp
from appliapps.tpp.fdr import get_iprob_for_fdr


class ProteinProphet(WrappedApp):
    """
    Wrapper for TPP-tool ProteinProphet.
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE),

            Argument(Keys.PEPXML, KeyHelp.PEPXML),
            Argument('MAYUOUT','mayu out csv'),
            Argument('FDR_TYPE', "type of FDR: iprophet/mayu m/pep/protFDR"),
            Argument("FDR_CUTOFF", "cutoff for FDR"),
        ]

    def prepare_run(self, log, info):
        if isinstance(info[Keys.PEPXML], list):
            raise RuntimeError("This ProteinProphet only takes one iProphet inputfile!")

        info['IPROB'],info['FDR'] = get_iprob_for_fdr(info['FDR_CUTOFF'], info['FDR_TYPE'], mayuout=info.get('MAYUOUT'),
                                                      pepxml=info[Keys.PEPXML])

        info['PROTEINPROPHET'] = 'IPROPHET MINPROB%s' % info['IPROB']
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
    ProteinProphet.main()