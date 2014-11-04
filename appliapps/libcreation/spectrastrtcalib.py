#!/usr/bin/env python
import os
import re

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

            Argument('RUNRT', "Boolean to activate iRT calibration"),
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

        info['SPLOG'] = os.path.join(info[Keys.WORKDIR], 'spectrast.log')

        # get iProb corresponding FDR for IDFilter
        info['IPROB'], info['FDR'] = get_iprob_for_fdr(info['FDR_CUTOFF'], info['FDR_TYPE'],
                                                       mayuout=info.get('MAYUOUT'),
                                                       pepxml=info.get(Keys.PEPXML))

        if info.get("RUNRT") == "True":
            rtcorrect = "-c_IRT%s -c_IRR" % info['RTKIT']
        else:
            rtcorrect = ""

        rtcalib_base = os.path.join(info[Keys.WORKDIR], 'RTcalib')
        rtcalib = rtcalib_base + '.splib'


        consensustype = ""
        if info['CONSENSUS_TYPE'] == "Consensus":
            consensustype = "C"
        elif info['CONSENSUS_TYPE'] == "Best replicate":
            consensustype = "B"

        consensus_base = os.path.join(info[Keys.WORKDIR], 'consensus')
        consensus = consensus_base + '.splib'
        info['SPLIB'] = consensus

        command = "spectrast -L%s -c_RDYDECOY -cI%s -cP%s %s -cN%s %s && " \
                  "spectrast -L%s -c_BIN! -cA%s -cN%s %s" % (
                      info['SPLOG'], info['MS_TYPE'], info['IPROB'], rtcorrect, rtcalib_base, peplink,
                      info['SPLOG'], consensustype, consensus_base, rtcalib)

        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        # Spectrast imports sample also when not enough iRTs found. These entries have Comment: without iRT attribute
        notenough = set()
        for line in open(info['SPLIB']).readlines():
            if "Comment:" in line and not "iRT=" in line:
                sample = re.search("RawSpectrum=([^\.]*)\.", line).group(1)
                notenough.add(sample)
        if info['RUNRT'] == "True" and notenough:
            raise RuntimeError("Not enough iRT peptides found in sample(s): " + ", ".join(notenough))

        # Parse logfile to see whether RSQ is high enough
        # PEPXML IMPORT: RT normalization by linear regression. Found 4 landmarks in MS run "CHLUD_L110830_21".
        #PEPXML_IMPORT: Final fitted equation: iRT = (rRT - 1383) / (41.05); R^2 = 0.9995; 1 outliers removed.
        for line in open(info['SPLOG']).readlines():
            if "Final fitted equation:" in line:
                samplename = prevline.strip().split(" ")[-1]
                rsq = line.split()[-4].replace(";", "")
                if float(rsq) < float(info['RSQ_THRESHOLD']):
                    raise RuntimeError(
                        "R^2 of %s is below threshold of %s for %s!" % (rsq, info['RSQ_THRESHOLD'], samplename))
                else:
                    log.debug("R^2 of %s is OK for %s" % (rsq, samplename))
            else:
                prevline = line

        #Double check
        if not " without error." in stdout:
            raise RuntimeError("SpectraST finished with some error!")

        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['SPLIB'])
        return info


if __name__ == "__main__":
    SpectrastRTcalib.main()