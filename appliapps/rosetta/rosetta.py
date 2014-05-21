#!/usr/bin/env python
import os
import subprocess

from configobj import ConfigObj

from applicake.app import WrappedApp
from applicake.apputils import templates
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class Rosetta(WrappedApp):
    """
    Wrapper for minirosetta.default.linuxgcc
    """

    def add_args(self):
        return [
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE, default="minirosetta.default.linuxgccrelease"),
            Argument('DSSOUT', 'file list downloaded by dss'),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('ROSETTA_EXTRACTDIR', 'dir where rosetta dataset was extracted to'),
            Argument('N_MODELS','number of models to make, internally called n_struct'),

            Argument('RUN__PROTOCOL', '', default="threading"),
            Argument('RUN__SHUFFLE', '', default="TRUE"),
            Argument('CM__ALN_FORMAT', '', default="grishin"),
            Argument('IN__FILE__FULLATOM', '', default="TRUE"),
            Argument('IDEALIZE_AFTER_LOOP_CLOSE', '', default="TRUE"),
            Argument('OUT__FILE__SILENT_STRUCT_TYPE', '', default="binary"),
            Argument('LOOPS__EXTENDED', '', default="TRUE"),
            Argument('LOOPS__BUILD_INITIAL', '', default="TRUE"),
            Argument('LOOPS__REMODEL', '', default="quick_ccd"),
            Argument('LOOPS__RELAX', '', default="relax"),
            Argument('RELAX__FAST', '', default="TRUE"),
            Argument('RELAX__DEFAULT_REPEATS', '', default="16"),
            Argument('SILENT_DECOYTIME', '', default="TRUE"),
            Argument('RANDOM_GROW_LOOPS_BY', '', default="4"),
            Argument('SELECT_BEST_LOOP_FROM', '', default="1"),
            Argument('IN__DETECT_DISULF', '', default="false"),
            Argument('FAIL_ON_BAD_HBOND', '', default="false"),
            Argument('BGDT', '', default="TRUE"),
            Argument('EVALUATION__GDTMM', '', default="TRUE")
        ]

    def prepare_run(self, log, info):
        for f in info['DSSOUT']:
            if "dataset.properties" in f:
                dsprop = ConfigObj(f)

        info["SEQ"] = dsprop["SEQ"]
        info["IN__FILE__ALIGNMENT"] = os.path.join(info["ROSETTA_EXTRACTDIR"], dsprop["ALIGNMENT_FILE"])
        info["IN__FILE__FASTA"] = os.path.join(info["ROSETTA_EXTRACTDIR"], dsprop["FILE_STEM"] + ".fasta")
        info["FRAG3"] = os.path.join(info["ROSETTA_EXTRACTDIR"], dsprop["3MERS"])
        info["FRAG9"] = os.path.join(info["ROSETTA_EXTRACTDIR"], dsprop["9MERS"])
        info["LOOPS__FRAG_SIZES"] = "9 3 1"
        info["LOOPS__FRAG_FILES"] = info["FRAG9"] + " " + info["FRAG3"] + " none"
        info["IN__FILE__PSIPRED_SS2"] = os.path.join(info["ROSETTA_EXTRACTDIR"], dsprop["FILE_STEM"] + ".psipred_ss2")
        info['ROSETTA_OUT'] = os.path.join(info[Keys.WORKDIR], 'default.out')
        #needed because of rosetta && gzip
        info['ROSETTA_COMPRESSEDOUT'] = info['ROSETTA_OUT'] + '.gz'

        info["IN__FILE__TEMPLATE_PDB"] = ""
        for pdb in dsprop["TEMPLATES"].split():
            info["IN__FILE__TEMPLATE_PDB"] += os.path.join(info["ROSETTA_EXTRACTDIR"], pdb) + " "
        info["IN__FILE__TEMPLATE_PDB"] = info["IN__FILE__TEMPLATE_PDB"].strip()

        info["DATABASE"] = os.environ["ROSETTA3_DB"]
        info["ROSETTA_VERSION"] = subprocess.check_output("which %s | cut -d/ -f5" % info[Keys.EXECUTABLE],
                                                          shell=True).strip()
        info["INFRASTRUCTURE"] = "BRUTUS"

        #change the on/off flags only in the template, not the info  
        app_info = info.copy()
        app_info['RUN__SHUFFLE'] = "-run:shuffle" if info['RUN__SHUFFLE'] == "TRUE" else ""
        app_info['IN__FILE__FULLATOM'] = "-in:file:fullatom" if info['IN__FILE__FULLATOM'] == "TRUE" else ""
        app_info['IDEALIZE_AFTER_LOOP_CLOSE'] = "-idealize_after_loop_close" if info[
                                                                                    'IDEALIZE_AFTER_LOOP_CLOSE'] == "TRUE" else ""
        app_info['LOOPS__EXTENDED'] = "-loops:extended" if info['LOOPS__EXTENDED'] == "TRUE" else ""
        app_info['LOOPS__BUILD_INITIAL'] = "-loops:build_initial" if info['LOOPS__BUILD_INITIAL'] == "TRUE" else ""
        app_info['RELAX__FAST'] = "-relax:fast" if info['RELAX__FAST'] == "TRUE" else ""
        app_info['SILENT_DECOYTIME'] = "-silent_decoytime" if info['SILENT_DECOYTIME'] == "TRUE" else ""
        app_info['BGDT'] = "-bGDT" if info['BGDT'] == "TRUE" else ""
        app_info['EVALUATION__GDTMM'] = "-evaluation:gdtmm" if info['EVALUATION__GDTMM'] == "TRUE" else ""

        tpl = os.path.join(info[Keys.WORKDIR], "flags")
        templates.read_mod_write(app_info, templates.get_tpl_of_class(self), tpl)

        command = "%s @%s && gzip %s" % (app_info[Keys.EXECUTABLE], tpl, app_info['ROSETTA_OUT'])
        return info, command


if __name__ == "__main__":
    Rosetta.main()
