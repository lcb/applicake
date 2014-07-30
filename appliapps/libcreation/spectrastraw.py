#!/usr/bin/env python
import os

from appliapps.tpp.fdr import get_iprob_for_fdr
from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class RawTxtlibNodecoy(WrappedApp):
    """
    Create raw text library without DECOYS_ from pepxml 
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.MZXML, KeyHelp.MZXML),

            Argument(Keys.PEPXML, KeyHelp.PEPXML),
            Argument('MAYUOUT', 'mayu out csv'),
            Argument('FDR_TYPE', "type of FDR: iprophet/mayu m/pep/protFDR"),
            Argument("FDR_CUTOFF", "cutoff for FDR"),

            Argument('MS_TYPE', 'ms instrument type')
        ]

    def prepare_run(self, log, info):
        # have to symlink the pepxml and mzxml files first into a single directory
        peplink = os.path.join(info[Keys.WORKDIR], os.path.basename(info[Keys.PEPXML]))
        log.debug('create symlink [%s] -> [%s]' % (info[Keys.PEPXML], peplink))
        os.symlink(info[Keys.PEPXML], peplink)

        if isinstance(info[Keys.MZXML], list):
            mzxmlslinks = info[Keys.MZXML]
        else:
            mzxmlslinks = [info[Keys.MZXML]]
        for f in mzxmlslinks:
            dest = os.path.join(info[Keys.WORKDIR], os.path.basename(f))
            log.debug('create symlink [%s] -> [%s]' % (f, dest))
            os.symlink(f, dest)

        #get iProb corresponding FDR for IDFilter
        info['IPROB'],info['FDR'] = get_iprob_for_fdr(info['FDR_CUTOFF'], info['FDR_TYPE'], mayuout=info['MAYUOUT'],
                                                      pepxml=info[Keys.PEPXML])

        basename = os.path.join(info[Keys.WORKDIR], 'RawTxtlibNodecoy')

        command = "spectrast -c_BIN! -cf'Protein!~DECOY_' -cP%s -cI%s -cN%s %s" % (
            info['IPROB'], info['MS_TYPE'], basename, peplink)

        info['SPLIB'] = basename + '.splib'

        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['SPLIB'])
        return info


if __name__ == "__main__":
    RawTxtlibNodecoy.main()