#!/usr/bin/env python
import os

from applicake.app import BasicApp
from applicake.apputils import dicts
from applicake.coreutils.arguments import Argument
import applicake.coreutils.info as infohandler
from applicake.coreutils.keys import Keys, KeyHelp


class EngineCollate(BasicApp):
    """
    Required because guse cannot collate conditional branches, it can only collect all at once
    """

    def add_args(self):
        return [
            Argument('ENGINES', 'Engines available for doing search'),
            Argument(Keys.MERGED, KeyHelp.MERGED),
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
        ]

    def run(self, log, info):
        used_engines = []
        log.debug("Available engines: %s", info['ENGINES'])
        for engine in info['ENGINES'].split(" "):
            key = 'RUN' + engine.upper()
            if key in info and info[key] == 'True':
                used_engines.append(engine)
        log.debug("Used engines: %s" % used_engines)

        runs = len(info[Keys.DATASET_CODE])
        for i in range(runs):
            collectedconfig = {}
            for engine in used_engines:
                path = "%s.ini_%d" % (engine, i)
                if not os.path.exists(path):
                    raise RuntimeError("Required inifile not found " + path)
                engineconfig = infohandler.get_handler(path).read(path)
                collectedconfig = dicts.merge(collectedconfig, engineconfig, priority='append')

            for key in collectedconfig.keys():
                if isinstance(collectedconfig[key], list):
                    collectedconfig[key] = dicts.unify(collectedconfig[key])

            collector_path = "%s_%d" % (info[Keys.MERGED], i)
            infohandler.get_handler(info[Keys.MERGED]).write(collectedconfig, collector_path)
            log.debug('Wrote outfile ' + collector_path)

        return info


if __name__ == "__main__":
    EngineCollate.main()