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
            Argument('CHROM_MZML', 'the chrom.mzml to requant'),
            Argument('ALIGNMENT_TSV', 'featurealigner outfile'),
            Argument('TRAFO_FILES', 'all tr files'),

            Argument('BORDER_OPTION', '', default='median'),
        ]

    def prepare_run(self, log, info):
        if info.get('DO_CHROMML_REQUANT', "") == "false":
            log.warning("Found flag, skipping requantification!")
            return info, "true"

        tdir = os.environ.get("TMPDIR", info[Keys.WORKDIR])
        #split off .gz suffix
        localmzml = os.path.join(tdir, os.path.basename(info["CHROM_MZML"])[:-3])

        mzmlroot = os.path.basename(info["CHROM_MZML"]).split(".")[0]
        localtr = ""
        trlist = []
        if not isinstance(info["TRAFO_FILES"], list):
            info["TRAFO_FILES"] = [info["TRAFO_FILES"]]
        for i in info["TRAFO_FILES"]:
            #the tr corresponding to mzml is linked to tdir
            if mzmlroot in i:
                localtr = os.path.join(tdir, os.path.basename(i))
                os.symlink(i, localtr)
                trlist.append(localtr)
            #the other trs are added to list
            else:
                trlist.append(i)
        if not localtr:
            raise RuntimeError("No correspondin tr found for " + mzmlroot)

        info['REQUANT_TSV'] = os.path.join(info[Keys.WORKDIR], "requant.tsv")

        command = "gunzip -c %s > %s && " \
                  "requantAlignedValues.py --disable_isotopic_transfer --in %s --peakgroups_infile %s --do_single_run %s --out %s " \
                  "--border_option %s " % (
                      info["CHROM_MZML"], localmzml,
                      " ".join(trlist), info['ALIGNMENT_TSV'], localtr, info['REQUANT_TSV'],
                      info['BORDER_OPTION'])

        return info, command


    def validate_run(self, log, info, exit_code, stdout):
        validation.check_stdout(log, stdout)
        validation.check_exitcode(log, exit_code)
        if info.get('DO_CHROMML_REQUANT', "") != "false":
            validation.check_file(log, info['REQUANT_TSV'])
        return info


if __name__ == "__main__":
    RequantValues.main()