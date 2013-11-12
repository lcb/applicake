"""
Created on Oct 24, 2012

phl1: 1.7G => 9min 12G => 256MB
phl2: 2GB => 12min 14G => 560MB
set pub.1h 15G RAM

@author: lorenz
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils

class ConvertTramlToTsv(IWrapper):

    def prepare_run(self, info, log):
        info['TRAML_CSV'] = os.path.join(info[Keys.WORKDIR],os.path.basename(info['TRAML'])+".csv")

        command = 'ConvertTraMLToTSV -no_progress -in %s -out %s' % (info['TRAML'], info['TRAML_CSV'])
        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, 'WORKDIR', 'wd')
        args_handler.add_app_args(log, 'TRAML', 'traml')
        args_handler.add_app_args(log,"DATASET_CODE","")
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        resultfile = info['TRAML_CSV']
        if not FileUtils.is_valid_file(log, resultfile):
            log.critical('%s is not valid', resultfile)
            return 1, info

        if 37 * os.path.getsize(info["TRAML_CSV"]) * len(info["DATASET_CODE"]) > 5*1024*1024*1024*1024:
            log.warn("Your workflow is too big, skipping requantification!")
            info["DO_CHROMML_REQUANT"] = "false"

        return run_code, info
