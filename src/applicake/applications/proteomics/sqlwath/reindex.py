#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: loblum
"""
import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils



class ReindexMzxml(IWrapper):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'executable to run', default="msconvert")
        
        args_handler.add_app_args(log, Keys.WORKDIR, "")
        args_handler.add_app_args(log, "DSSOUTPUT", "")
        args_handler.add_app_args(log, Keys.MZXML, "")
        args_handler.add_app_args(log, Keys.THREADS, "")
        
        args_handler.add_app_args(log, "RESOLUTION", "")
        args_handler.add_app_args(log, "MZSCALE", "")
        args_handler.add_app_args(log, "RTSCALE", "")
        args_handler.add_app_args(log, "MZWIDTH", "")
        args_handler.add_app_args(log, "RTWIDTH", "")
        args_handler.add_app_args(log, "MININTENSITY", "")
        args_handler.add_app_args(log, "MASSRANGE", "")
        return args_handler

    def prepare_run(self, info, log):
        #in case getdataset instead of getmsdata was used key MZXML is not set but mzXML.gz is in DSSOUTPUT list
        if not Keys.MZXML in info:
            log.info("No key MZXML found, getting from DSSOUTPUT list")
            for key in info[Keys.DSSOUTPUT]:
                if '.mzXML' in key:
                    info[Keys.MZXML] = key

        infile =info['MZXML']
        base =info['MZXML'].split("/")[-1].split(".")[0]
        info['MZXML'] = os.path.join(info[Keys.WORKDIR], base + ".mzXML")
        command = "%s --outdir %s --mzXML -z %s" % (info[Keys.PREFIX],info[Keys.WORKDIR],infile)
        return command, info

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info
        outfile = info['MZXML']
        if not FileUtils.is_valid_file(log, outfile):
            return 1, info
        return 0, info

