import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils


class FeatureAlignment(IWrapper):
    _outfiles = []

    def prepare_run(self, info, log):
        info['ALIGNMENT_TSV'] = os.path.join(info['WORKDIR'], "feature_alignment.tsv")
        info['ALIGNMENT_MATRIX'] = os.path.join(info['WORKDIR'], "feature_alignment_matrix.tsv")
        if not isinstance(info["MPROPHET_TSV"], list):
            info["MPROPHET_TSV"] = [info["MPROPHET_TSV"]]

        realignruns = ""
        if info["ALIGNER_REALIGNRUNS"] == "true":
            realignruns = "--realign_runs"

        command = "feature_alignment.py --file_format openswath --fdr_cutoff %s --max_rt_diff %s --max_fdr_quality %s --method %s --frac_selected %s %s --out %s --out_matrix %s --in %s" % (
            info['ALIGNER_FDR'],
            info['ALIGNER_MAX_RTDIFF'],
            info['ALIGNER_MAX_FDRQUAL'],
            info['ALIGNER_METHOD'],
            info['ALIGNER_FRACSELECTED'],
            realignruns,
            info['ALIGNMENT_TSV'],
            info['ALIGNMENT_MATRIX'],
            " ".join(info["MPROPHET_TSV"]))
        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'ALIGNER_FDR', '')
        args_handler.add_app_args(log, 'ALIGNER_MAX_RTDIFF', '')
        args_handler.add_app_args(log, 'ALIGNER_MAX_FDRQUAL', '')
        args_handler.add_app_args(log, 'ALIGNER_METHOD', '')
        args_handler.add_app_args(log, 'ALIGNER_FRACSELECTED', '')
        args_handler.add_app_args(log, 'ALIGNER_REALIGNRUNS', '')

        args_handler.add_app_args(log, 'MPROPHET_TSV', '')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info
        if not FileUtils.is_valid_file(log, info['ALIGNMENT_TSV']):
            return 1, info
        if not FileUtils.is_valid_file(log, info['ALIGNMENT_MATRIX']):
            return 1, info

        return 0, info
    
