#!/usr/bin/env python
import os

from appliapps.tpp.fdr import get_iprob_for_fdr
from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class SpectrastRTcalib(WrappedApp):
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

            Argument('RTCALIB_TYPE', "iRT calibration type [linear/spline/none]"),
            Argument('RTKIT', 'RT kit (file)'),
            Argument('MS_TYPE', 'ms instrument type'),
            Argument('CONSENSUS_TYPE', 'consensus type cAC cAB'),
        ]

    def prepare_run(self, log, info):
        # symlink the pepxml and mzxml files first into a single directory
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

        consensustype = ""  # None
        if info['CONSENSUS_TYPE'] == "Consensus":
            consensustype = "C"
        elif info['CONSENSUS_TYPE'] == "Best replicate":
            consensustype = "B"

        # get iProb corresponding FDR for IDFilter
        info['IPROB'], info['FDR'] = get_iprob_for_fdr(info['FDR_CUTOFF'], info['FDR_TYPE'],
                                                       mayuout=info.get('MAYUOUT'),
                                                       pepxml=info.get(Keys.PEPXML))

        if info.get("RTCALIB_TYPE") == "spline":
            rtcorrect = "-c_IRT%s " % info['RTKIT']
        elif info.get("RTCALIB_TYPE") == "linear":
            rtcorrect = "-c_IRT%s -c_IRR" % info['RTKIT']
        else:
            rtcorrect = ""

        basename = os.path.join(info[Keys.WORKDIR], 'SpectrastNodecoyRTcalib')

        command = "spectrast -c_BIN! -c_RDYDECOY -cI%s -cP%s -cA%s %s -cN%s %s" % (
            info['MS_TYPE'], info['IPROB'], consensustype, rtcorrect, basename, peplink)

        info['SPLIB'] = basename + '.splib'

        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        notenough = ""
        prevline = ""
        for line in open("spectrast.log").readlines():
            if "Too few landmarks with distinct iRTs to perform RT normalization." in line:
                notenough += prevline.split(" ")[-2] + " "
            prevline = line
        if notenough:
            raise RuntimeError("Not enough iRT peptides found in samples: " + notenough)
        if not " without error." in stdout:
            raise RuntimeError("SpectraST finished with errors!")
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['SPLIB'])
        return info


if __name__ == "__main__":
    SpectrastRTcalib.main()