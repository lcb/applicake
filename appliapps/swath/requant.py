#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class RequantValues(WrappedApp):
    """
    requant needs the chrom.mzml unzipped, the corresponding tr in same dir and the remaining *tr to adjust
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),

            Argument('DO_CHROMML_REQUANT', 'to skip set to false'),
            Argument('ALIGNMENT_TSV', 'featurealigner outfile'),
            Argument('CHROM_MZML', 'the chrom.mzml to requant'),
            Argument('TRAFO_FILES', 'all tr files'),

            Argument('ALIGNER_METHOD','for checking only'),
            Argument('ALIGNER_REALIGN_METHOD', 'featurealingn+requant: RT realign method. req for SingleShortestPath'),
            Argument('ISOTOPIC_GROUPING', 'featurealingn+requant: enable/disable isotopic grouping'),
            Argument('ISOTOPIC_TRANSFER', 'requant only: do isotopic transfer'),
            Argument('REQUANT_METHOD', ''),

        ]

    def prepare_run(self, log, info):
        if info.get('DO_CHROMML_REQUANT', "") == "false":
            log.warning("Found flag, skipping requantification!")
            return info, "true"

        if isinstance(info["CHROM_MZML"],list):
            raise RuntimeError("Only one chrom.mzML file per job allowed!")

        #decompress chrom.mzML.gz to TMPDIR on-the-fly w/o .gz suffix
        tdir = os.environ.get("TMPDIR", info[Keys.WORKDIR])
        localmzml = os.path.join(tdir, os.path.basename(info["CHROM_MZML"])[:-3])
        info['REQUANT_TSV'] = os.path.join(info[Keys.WORKDIR], "requant.tsv")

        flags = ''
        if info['ISOTOPIC_GROUPING'] == "false":
            flags += " --disable_isotopic_grouping "
        if info['ISOTOPIC_TRANSFER'] == "false":
            flags += " --disable_isotopic_transfer "
        flags += " --realign_runs %s " % info['ALIGNER_REALIGN_METHOD']
        flags += " --method %s " % info['REQUANT_METHOD']
        #when method allTrafo is set --in *.tr must be set and the tr corresponding to the current chrom.mzML must be
        #linked to TMPDIR
        if info['REQUANT_METHOD'] == "allTrafo":
            if "LocalMST" in info['ALIGNER_METHOD']:
                raise RuntimeError("Boundary method 'allTrafo' does not work with feature aligner clustering method "
                                   "'LocalMST', use 'singleShortest*' instead")
            mzmlroot = os.path.basename(info["CHROM_MZML"]).split(".")[0]
            localtr = ""
            trlist = []
            if not isinstance(info["TRAFO_FILES"], list):
                info["TRAFO_FILES"] = [info["TRAFO_FILES"]]
            for i in info["TRAFO_FILES"]:
                #the tr corresponding to mzml is linked to tdir
                if mzmlroot+"_with_dscore" in i:
                    localtr = os.path.join(tdir, os.path.basename(i))
                    os.symlink(i, localtr)
                    trlist.append(localtr)
                #the other trs are added to list
                else:
                    trlist.append(i)
            if not localtr:
                raise RuntimeError("No corresponding tr found for " + mzmlroot)
            flags += " --in %s --do_single_run %s" % (" ".join(trlist),localtr)
        else:
            #for singleShortestPath or singleClosest*
            flags += " --do_single_run %s " % localmzml

        command = "gunzip -c %s > %s && " \
                  "requantAlignedValues.py --peakgroups_infile %s --out %s %s" % (
                      info["CHROM_MZML"], localmzml,
                      info['ALIGNMENT_TSV'], info['REQUANT_TSV'], flags)

        return info, command


    def validate_run(self, log, info, exit_code, stdout):
        validation.check_stdout(log, stdout)
        validation.check_exitcode(log, exit_code)
        if info.get('DO_CHROMML_REQUANT', "") != "false":
            validation.check_file(log, info['REQUANT_TSV'])
        return info


if __name__ == "__main__":
    RequantValues.main()