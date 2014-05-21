#!/usr/bin/env python
import os
from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys,KeyHelp


class BioPersonalDB(WrappedApp):
    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument("DB_SOURCE", 'BioDB or PersonalDB'),
            Argument("DBASE", 'Filepath (BioDB) or an openbis-dataset-code (PersonalDB)'),
            Argument("DATASET_DIR", 'dataset cache')
        ]

    def prepare_run(self, log, info):
        if info["DB_SOURCE"] == "BioDB":
            command = "true"
        elif info["DB_SOURCE"] == "PersonalDB":
            self.rfile = os.path.join(info[Keys.WORKDIR],"getdataset.out")
            command = "getdataset -v -r %s -o %s %s" % (self.rfile, info["DATASET_DIR"], info["DBASE"])
        else:
            raise RuntimeError("Unkwnown DB_SOURCE " + info["DB_SOURCE"])
        return info, command

    def validate_run(self, log, info, run_code, out):
        validation.check_exitcode(log,run_code)

        if info["DB_SOURCE"] == "BioDB":
            log.info("Database remains " + info["DBASE"])
        else:
            f = open(self.rfile)
            found = False
            for line in f.readlines():
                #if info['DB_TYPE'].lower in line.lower():
                if '.fasta' in line.lower() or '.txt' in line.lower():
                    info['DBASE'] = line.split()[1]
                    log.info("Database found " + info["DBASE"])
                    found = True
                if '.traml' in line.lower():
                    info['TRAML'] = line.split()[1]
                    log.info("TraML found " + info["TRAML"])
                    found = True
            f.close()
            if not found:
                log.error("No matching database (.fasta or .traml) found in dataset!")
                return info

        return info

if __name__ == "__main__":
    BioPersonalDB.main()