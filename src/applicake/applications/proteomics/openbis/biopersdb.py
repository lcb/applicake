#!/usr/bin/env python
"""
Created on 7 Jun 2013

@author: lorenz
"""

from applicake.framework.interfaces import IWrapper
from applicake.framework.keys import Keys

class BioPersonalDB(IWrapper):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.WORKDIR, 'workdir')
        args_handler.add_app_args(log, "DB_SOURCE", 'workdir')
        args_handler.add_app_args(log, "DBASE", 'workdir')
        return args_handler

    def prepare_run(self, info, log):
        if info["DB_SOURCE"] == "BioDB":
            command = "true"
        elif info["DB_SOURCE"] == "PersonalDB":
            command = "getdataset -r getdataset.out -o %s %s" % (info["WORKDIR"], info["DBASE"])
        else:
            raise Exception("Unkwnown DB_SOURCE " + info["DB_SOURCE"])
        return command, info

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info

        if info["DB_SOURCE"] == "BioDB":
            pass
        else:
            f = open("getdataset.out")
            for line in f.readlines():
                #if info['DB_TYPE'].lower in line.lower():
                if 'fasta' in line.lower():
                    info['DBASE'] = line.split()[1]
                if 'traml' in line.lower():
                    info['TRAML'] = line.split()[1]
                    log.info("TraML is "+info["TRAML"])
            f.close()
                    
        log.info("Database is "+info["DBASE"])
        return run_code, info
