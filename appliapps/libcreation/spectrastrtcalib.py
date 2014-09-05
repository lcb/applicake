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
            Argument('RSQ_THRESHOLD', 'specify r-squared threshold to accept linear regression'),
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

        if info.get("RTCALIB_TYPE") == "linear":
            rtcorrect = "-c_IRT%s -c_IRR" % info['RTKIT']
        else:
            rtcorrect = ""

        basename = os.path.join(info[Keys.WORKDIR], 'SpectrastNodecoyRTcalib')
        info['SPLOG'] = basename + '.log'

        command = "spectrast -L%s -c_BIN! -c_RDYDECOY -cI%s -cP%s -cA%s %s -cN%s %s" % (
            info['SPLOG'],info['MS_TYPE'], info['IPROB'], consensustype, rtcorrect, basename, peplink)

        info['SPLIB'] = basename + '.splib'

        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        #Some entries are only found in logfile, not in stdout
        notenough = []
        prevline = None
        for line in open(info['SPLOG']).readlines():
            if "Final fitted equation:" in line:
                #PEPXML IMPORT: RT normalization by linear regression. Found 4 landmarks in MS run "CHLUD_L110830_21".
                #PEPXML_IMPORT: Final fitted equation: iRT = (rRT - 1383) / (41.05); R^2 = 0.9995; 1 outliers removed.
                samplename = prevline.strip().split(" ")[-1]
                rsq = line.split()[-4].replace(";", "")
                if float(rsq) < float(info['RSQ_THRESHOLD']):
                    raise RuntimeError("R^2 of %s is below threshold of %s for %s!" % (rsq, info['RSQ_THRESHOLD'],samplename))
                else:
                    log.debug("R^2 of %s is OK for %s" % (rsq,samplename))

            if "Too few landmarks with distinct iRTs to perform RT normalization." in line:
                #PEPXML IMPORT: RT normalization by linear regression. Found 1 landmarks in MS run "CHLUD_L110830_17".
                #ERROR PEPXML IMPORT: Too few landmarks with distinct iRTs to perform RT normalization.
                samplename = prevline.strip().split(" ")[-1]
                notenough.append(samplename)
            else:
                prevline = line
        if notenough:
            raise RuntimeError("Not enough iRT peptides found in samples " + str(notenough))

        if 'Advanced option "-c_RDYDECOY is undefined. Ignored.' in stdout:
                raise RuntimeError("Old spectrast version used which cannot do iRT calibration!")

        if not " without error." in stdout:
            raise RuntimeError("SpectraST finished with errors!")

        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['SPLIB'])
        return info


if __name__ == "__main__":
    SpectrastRTcalib.main()