"""
Created on Oct 24, 2012

@author: lorenz
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils


class pyProphet(IWrapper):
    _projectname = ''

    def prepare_run(self, info, log):

        command = 'mProphetScoreSelector.sh %s %s %s && pyprophet --target.dir=%s --xeval.num_iter=%s --xeval.numprocesses=%s %s' % (
        info['FEATURETSV'], info['MPR_MAINVAR'], info['MPR_VARS'],
        info['WORKDIR'], info['MPR_NUM_XVAL'], info['THREADS'],info['FEATURETSV'])
        return command, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, 'WORKDIR', 'wd')
        args_handler.add_app_args(log, 'THREADS', 'number of threads',default='1')
        args_handler.add_app_args(log, 'MPR_NUM_XVAL', 'help')
        args_handler.add_app_args(log, 'FEATURETSV', 'featuretsv')
        args_handler.add_app_args(log, 'MPR_MAINVAR', 'mProphet main score')
        args_handler.add_app_args(log, 'MPR_VARS', 'mProphet other scores')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):

        resultfile =  os.path.splitext(os.path.basename(info['FEATURETSV']))[0]+ "_with_dscore.csv"
        resultfile = os.path.join(info[Keys.WORKDIR], resultfile)
        if not FileUtils.is_valid_file(log, resultfile):
            log.critical('%s is not valid', resultfile)
            return 1, info
        else:
            info['MPROPHET_TSV'] = resultfile

        return run_code, info
