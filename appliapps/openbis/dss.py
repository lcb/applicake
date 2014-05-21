#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class Dss(WrappedApp):
    """
    The DSS is often a initial workflow node. Requesting a workdir has thus the nice side effect
    that the DSS generates the JOB_ID for the workflow
    """
    ALLOWED_PREFIXES = ['getdataset', 'getmsdata', 'getexperiment']
    TRUES = ['TRUE', 'T', 'YES', 'Y', '1']

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.EXECUTABLE, "%s %s" % (KeyHelp.EXECUTABLE, self.ALLOWED_PREFIXES)),
            Argument(Keys.DATASET_CODE, 'dataset code to get for getdataset or getmsdata'),
            Argument('EXPERIMENT', 'experiment code to get for for getexperiment'),
            Argument('DATASET_DIR', 'cache directory'),
            Argument('DSS_KEEP_NAME', "for 'getmsdata' only: output keeps original file name if set to true "
                                      "(otherwise it will be changed to samplecode~dscode.mzXXML)",
                     default='false')
        ]

    def prepare_run(self, log, info):
        executable = info[Keys.EXECUTABLE]
        if not executable in self.ALLOWED_PREFIXES:
            raise Exception("Executable %s must be one of [%s]" % (executable, self.ALLOWED_PREFIXES))

        self.rfile = os.path.join(info[Keys.WORKDIR], executable + ".out")

        outdir = info['DATASET_DIR']

        if executable == 'getmsdata' and not info['DSS_KEEP_NAME'].upper() == 'TRUE':
            koption = '-c'
        else:
            koption = ''

        if info[Keys.EXECUTABLE] == 'getexperiment':
            dscode_to_get = info['EXPERIMENT']
        else:
            dscode_to_get = info[Keys.DATASET_CODE]

        command = "%s -v -r %s --out=%s %s %s" % (executable, self.rfile, outdir, koption, dscode_to_get)
        return info, command

    def validate_run(self, log, info, exit_code, out):
        validation.check_exitcode(log, exit_code)

        #KEY where to store downloaded file paths
        default_keys = {'getmsdata': 'MZXML', 'getexperiment': 'SEARCH', 'getdataset': 'DSSOUT'}
        key = default_keys[info[Keys.EXECUTABLE]]
        #VALUE is a list of files or the mzXMLlink
        dsfls = []
        with open(self.rfile) as f:
            for downloaded in [line.strip() for line in f.readlines()]:
                ds, fl = downloaded.split("\t")
                if ds == info[Keys.DATASET_CODE] or ds == info['EXPERIMENT']:
                    dsfls.append(fl)

        #MZXML is expected only 1
        if key == 'MZXML':
            dsfls = dsfls[0]

        log.debug("Adding %s to %s" % (dsfls, key))
        info[key] = dsfls
        return info


if __name__ == "__main__":
    Dss.main()