#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: loblum
"""
import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils



class Mzxml2Sql(IWrapper):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'executable to run', default="findMF")
        
        args_handler.add_app_args(log, Keys.WORKDIR, "")
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
                    
        base =info['MZXML'].split("/")[-1].split(".")[0]
        info['MZSQL'] = os.path.join(info[Keys.WORKDIR], base + "_0.sqlite")
        
        min,max = info['MASSRANGE'].split("-")
        command = "%s --in %s --out %s --nrthreads %s --resolution %s --mzscale %s --rtscale %s --width-MZ %s --width-RT %s --minintensity %s --minMass %s --maxMass %s" % (
                    info[Keys.PREFIX],info['MZXML'],info[Keys.WORKDIR],info['THREADS'],info['RESOLUTION'],info['MZSCALE'],info['RTSCALE'],info['MZWIDTH'],info['RTWIDTH'],
                    info['MININTENSITY'],min,max)
        return command, info

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info
        outfile = info['MZSQL']
        if not FileUtils.is_valid_file(log, outfile):
            return 1, info
        return 0, info

