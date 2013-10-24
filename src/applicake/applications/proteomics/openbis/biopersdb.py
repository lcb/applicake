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
        args_handler.add_app_args(log, "DATASET_DIR", 'dataset cache')

        return args_handler

    def prepare_run(self, info, log):
        if info["DB_SOURCE"] == "BioDB":
            command = "true"
        elif info["DB_SOURCE"] == "PersonalDB":
            command = "getdataset -r getdataset.out -o %s %s" % (info["DATASET_DIR"], info["DBASE"])
        else:
            raise Exception("Unkwnown DB_SOURCE " + info["DB_SOURCE"])
        return command, info

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info

        if info["DB_SOURCE"] == "BioDB":
            log.info("Database remains "+info["DBASE"])
        else:
            f = open("getdataset.out")
            found = False
            for line in f.readlines():
                #if info['DB_TYPE'].lower in line.lower():
                if '.fasta' in line.lower():
                    info['DBASE'] = line.split()[1]
                    log.info("Database found "+info["DBASE"])
                    found = True
                if '.traml' in line.lower():
                    info['TRAML'] = line.split()[1]
                    log.info("TraML found "+info["TRAML"])
                    found = True
            f.close()
            if not found:
                log.error("No matching database (.fasta or .traml) found in dataset!")
                return 1,info

        return run_code, info
