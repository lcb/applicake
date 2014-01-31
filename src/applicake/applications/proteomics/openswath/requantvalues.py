"""
Created on Aug 10, 2012

200 sample with small lib:
8cpu, 3h7m, 4G RAM total, 200M scratch

@author: lorenz
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils


class RequantValues(IWrapper):
    _outfiles = []

    def prepare_run(self, info, log):
        if info.get('DO_CHROMML_REQUANT',"") == "false":
            log.warning("Found flag, skipping requantification!")
            return "true", info

        intsv = info['ALIGNMENT_TSV']

        localtrs = []
        #dont do comparison if only one mzml
        if not isinstance(info["CHROMML_GZ"], list):
            info["CHROMML_GZ"] = [info["CHROMML_GZ"]]
        if not isinstance(info["TRAFO_FILES"], list):
            info["TRAFO_FILES"] = [info["TRAFO_FILES"]]
        if len(info["CHROMML_GZ"]) != len(info["TRAFO_FILES"]):
            raise Exception("not same amount of mzML and tr files!")


        for i in range(len(info["TRAFO_FILES"])):
            idir = os.path.join(os.environ.get("TMPDIR", info[Keys.WORKDIR]),str(i))
            os.mkdir(idir)

            tr = info["TRAFO_FILES"][i]
            localtr = os.path.join(idir,os.path.basename(tr))
            os.symlink(tr,localtr)
            localtrs.append(localtr)

            mzml = info["CHROMML_GZ"][i]
            localmzml = os.path.join(idir,os.path.basename(mzml))
            os.symlink(mzml,localmzml)


        info['ALIGNMENT_TSV'] = os.path.join(info['WORKDIR'], "feature_alignment_requant.tsv")
        info['ALIGNMENT_MATRIX'] = os.path.join(info['WORKDIR'], "feature_alignment_requant_matrix.tsv")

        command = "requantAlignedParallel.sh --in %s --peakgroups_infile %s --out %s --out_matrix %s " \
                  "--border_option %s --threads %s | grep -v 'does not cover full range'" % (
            " ".join(localtrs),
            intsv,
            info['ALIGNMENT_TSV'],
            info['ALIGNMENT_MATRIX'],
            info['BORDER_OPTION'],info['THREADS'])

        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'CHROMML_GZ', '')
        args_handler.add_app_args(log, 'ALIGNMENT_TSV', '')
        args_handler.add_app_args(log, 'ALIGNMENT_MATRIX', '')
        args_handler.add_app_args(log, 'TRAFO_FILES', '')
        args_handler.add_app_args(log, 'THREADS', '')


        args_handler.add_app_args(log, 'BORDER_OPTION', '',default='median')
        args_handler.add_app_args(log, 'DO_CHROMML_REQUANT', '')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info
        if not FileUtils.is_valid_file(log, info['ALIGNMENT_TSV']):
            return 1, info
        if not FileUtils.is_valid_file(log, info['ALIGNMENT_MATRIX']):
            return 1, info

        return 0, info

