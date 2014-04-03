"""
Created on Oct 24, 2012

200 sample small lib:
with dscore cutoff and external R: 2h20m, 5G RAM

@author: lorenz
"""

import os,glob
import shutil
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils


class FeatureAlignment(IWrapper):
    _outfiles = []

    def prepare_run(self, info, log):
        info['ALIGNMENT_TSV'] = os.path.join(info['WORKDIR'], "feature_alignment.tsv")
        info['ALIGNMENT_MATRIX'] = os.path.join(info['WORKDIR'], "feature_alignment_matrix."+info['MATRIX_FORMAT'])
        info['ALIGNMENT_YAML'] = os.path.join(info['WORKDIR'], "feature_alignment.yaml")
        if not isinstance(info["MPROPHET_TSV"], list):
            info["MPROPHET_TSV"] = [info["MPROPHET_TSV"]]

        tmpdir = os.environ.get('TMPDIR',info[Keys.WORKDIR]) + '/'

        dfilter = ""
        if "ALIGNER_DSCORE_CUTOFF" in info and info["ALIGNER_DSCORE_CUTOFF"] != "":
            dfilter = "--use_dscore_filter  --dscore_cutoff " + info["ALIGNER_DSCORE_CUTOFF"]

        oldfdr = ""
        if 'ALIGNER_MAX_FDRQUAL' in info and info['ALIGNER_MAX_FDRQUAL'] != "":
            oldfdr = "--max_fdr_quality " + str(info['ALIGNER_MAX_FDRQUAL'])
        if 'ALIGNER_FDR' in info and info['ALIGNER_FDR'] != "":
            oldfdr += " --fdr_cutoff " + str(info['ALIGNER_FDR'])

        command = "feature_alignment.py --use_external_r --file_format openswath --in %s --out %s --out_matrix %s " \
                  "--matrix_output_method full --realign_runs --max_rt_diff %s %s --method %s --frac_selected %s " \
                  "%s --target_fdr %s --tmpdir %s --out_meta %s" % (
            " ".join(info["MPROPHET_TSV"]),info['ALIGNMENT_TSV'],info['ALIGNMENT_MATRIX'],
            info['ALIGNER_MAX_RTDIFF'],oldfdr,info['ALIGNER_METHOD'],info['ALIGNER_FRACSELECTED'],
            dfilter, info['ALIGNER_TARGETFDR'],tmpdir,info['ALIGNMENT_YAML'])

        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'MPROPHET_TSV', '')
        args_handler.add_app_args(log, 'ALIGNER_METHOD', '')
        args_handler.add_app_args(log, 'ALIGNER_FRACSELECTED', '')
        args_handler.add_app_args(log, 'ALIGNER_MAX_RTDIFF', '')
        args_handler.add_app_args(log, 'ALIGNER_TARGETFDR', '', default=-1)
        args_handler.add_app_args(log, 'ALIGNER_DSCORE_CUTOFF', 'if not set dont filter. if set use dscore cutoff')
        args_handler.add_app_args(log, 'MATRIX_FORMAT', '',default="xls")

        #use targetfdr options instead!
        args_handler.add_app_args(log, 'ALIGNER_FDR', '')
        args_handler.add_app_args(log, 'ALIGNER_MAX_FDRQUAL', '')
        args_handler.add_app_args(log, 'ALIGNER_REALIGNRUNS', 'true=realign, false=use iRT. faster but less accurate',default="true")

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info
        if not FileUtils.is_valid_file(log, info['ALIGNMENT_TSV']):
            return 1, info
        if not FileUtils.is_valid_file(log, info['ALIGNMENT_MATRIX']):
            return 1, info

        out2log = os.path.join(info[Keys.WORKDIR],"feature_alignment.out.txt")
        f = open(out2log,"w")
        f.write(out_stream.read())
        f.close()
        info["ALIGNER_STDOUT"] = out2log

        #TRAFO ML PATCH
        info["TRAFO_FILES"] = []
        for fil in info["MPROPHET_TSV"]:
            trfile = glob.glob(os.path.dirname(fil) + "/*.tr")
            if len(trfile) != 1:
                log.error("More than one .tr file for "+fil)
                return 1,info
            trtgt = os.path.join(info['WORKDIR'],os.path.basename(trfile[0]))
            shutil.move(trfile[0],trtgt)
            info["TRAFO_FILES"].append(trtgt)

        return 0, info

