#!/usr/bin/env python
import applicake.apputils.dicts as dicts
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import get_handler
from applicake.app import BasicApp
from applicake.coreutils.keys import Keys, KeyHelp


class Collate(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.COLLATE, KeyHelp.COLLATE)
        ]

    def run(self, log, info):
        ih = get_handler(info[Keys.COLLATE])
        paths = info[Keys.COLLATE].split(" ")
        del info[Keys.COLLATE]
        collector_config = info.copy()

        #read in
        for path in paths:
            log.debug('collating file [%s]' % path)
            config = ih.read(path)
            collector_config = dicts.merge(collector_config, config, priority='append')

        #unify
        for key in collector_config.keys():
            collector_config[key] = dicts.unify(collector_config[key])

        #write back
        return collector_config


if __name__ == "__main__":
    Collate.main()