"""
Created on Apr 14, 2012

@author: loblum
"""

import os

from configobj import ConfigObj

from applicake.framework.keys import Keys

from applicake.framework.interfaces import IApplication
from applicake.utils.dictutils import DictUtils
from applicake.utils.sequenceutils import SequenceUtils
from applicake.framework.informationhandler import IniInformationHandler


class IniEngineCollector(IApplication):
    """
    Required because 
    1) guse cannot collate, it can only collect all at once
    2) there are some checks if searches went fine or error
    """

    def getUsedEngines(self, info, log):
        available_engines = info['ENGINES']
        log.debug("Available engines: %s" % available_engines)
        used_engines = []
        log.info(info)
        for engine in available_engines:
            key = 'RUN' + engine.upper()
            if key in info and info[key] == 'True':
                used_engines.append(engine)

        log.info("Expected search engine inis: %s" % used_engines)

        return used_engines

    def getNumberOfRuns(self, info, log):
        #cleanup necessary
        if info.has_key('ENGINES'):
            del info['ENGINES']

        runs = 1
        for key, value in info.items():
            if isinstance(value, list):
                log.debug("Runs: %d times %d (key %s)" % (runs, len(value), key))
                runs *= len(value)

        log.info("Expected number of inis: %d" % runs)
        return runs

    def unifyCleanInfo(self, info):
        for key in info.keys():
            if isinstance(info[key], list):
                info[key] = SequenceUtils.unify(info[key], reduce=True)

        if info.has_key(Keys.WORKDIR):
            del info[Keys.WORKDIR]
        return info

    def main(self, info, log):
    #TODO: simplify "wholeinfo" apps
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        used_engines = self.getUsedEngines(info, log)
        runs = self.getNumberOfRuns(info, log)

        for i in range(runs):

            collector_config = {}
            for engine in used_engines:
                path = "%s.ini_%d" % (engine, i)
                if not os.path.exists(path):
                    log.critical("Required inifile not found " + path)
                    return 1, info
                config = ConfigObj(path)
                collector_config = DictUtils.merge(log, collector_config, config, priority='append')

            unified_config = self.unifyCleanInfo(collector_config)
            collector_path = "%s_%d" % (info[Keys.GENERATOR], i)

            config = ConfigObj(unified_config)
            config.filename = collector_path
            config.write()
            log.info('Wrote outfile ' + collector_path)

        return 0, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, 'ENGINES', 'Engines available for doing search', action='append')
        args_handler.add_app_args(log, Keys.GENERATOR, 'Base name for generated files')

        #TODO: simplify "wholeinfo" apps
        args_handler.add_app_args(log, Keys.INPUT, 're-read input to access whole info')
        args_handler.add_app_args(log, Keys.BASEDIR, 'get basedir if set or modified by runner')
        args_handler.add_app_args(log, Keys.JOB_IDX, 'get jobidx if set or modified by runner')
        args_handler.add_app_args(log, Keys.STORAGE, 'get storage if set or modified by runner')
        args_handler.add_app_args(log, Keys.LOG_LEVEL, 'get loglevel if set or modified by runner')

        return args_handler

