#!/usr/bin/env python
import glob

import applicake.coreutils.info as infohandler
from applicake.app import BasicApp
from applicake.coreutils.arguments import Argument
from applicake.apputils import dicts
from applicake.coreutils.keys import Keys, KeyHelp


class Merge(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.MERGE, KeyHelp.MERGE),
            Argument(Keys.MERGED, KeyHelp.MERGED)
        ]

    def run(self, log, info):
        paths = sorted(glob.glob(info[Keys.MERGE] + "_*"))

        #read in
        config_container = {}
        nofiles = len(paths)
        if nofiles == 0:
            raise RuntimeError("No files to merge found!")
        for path in paths:
            log.debug("Reading " + path)
            config = infohandler.get_handler(path).read(path)

            lastjob = config[Keys.SUBJOBLIST][-1]
            checksum = int(lastjob.split(Keys.SUBJOBSEP)[2])
            if nofiles != checksum:
                raise RuntimeError("Number of inputfiles %d and checksum %d do not match" % (nofiles, checksum))

            #append the current config to the ones with same parent subjobs
            parentjoblist = config[Keys.SUBJOBLIST][:-1]
            parentjobstr = self.parentjobs_to_str(parentjoblist)

            #remove one level from subjoblist
            config[Keys.SUBJOBLIST] = parentjoblist
            if not config[Keys.SUBJOBLIST]:
                del config[Keys.SUBJOBLIST]
            if parentjobstr in config_container:
                config_container[parentjobstr] = dicts.merge(config_container[parentjobstr], config, priority='append')
            else:
                config_container[parentjobstr] = config

        #unify (only possible after all collected)
        for config in config_container.values():
            for key in config.keys():
                if key == Keys.SUBJOBLIST:
                    config[key] = dicts.unify(config[key], unlist_single=False)
                    continue
                if isinstance(config[key], list):
                    config[key] = dicts.unify(config[key])

        #write back
        for i, config in enumerate(config_container.values()):
            path = info[Keys.MERGED] + '_' + str(i)
            log.debug("Writing out " + path)
            infohandler.get_handler(path).write(config, path)

        return info

    @staticmethod
    def parentjobs_to_str(parentjobs):
        parent = Keys.SUBJOBSEP
        for subjob in parentjobs:
            parent += str(subjob.split(Keys.SUBJOBSEP)[0]) + Keys.SUBJOBSEP
        return parent


if __name__ == "__main__":
    Merge.main()