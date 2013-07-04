"""
Created on Apr 14, 2012

@author: quandtan
"""

import glob
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication
from applicake.framework.informationhandler import IniInformationHandler
from applicake.utils.dictutils import DictUtils


class IniCollector(IApplication):
    """
    Basic Collector which merges collector files by flatten the value sequence.
    """

    def get_collector_files(self, info):
        """
        Return all input files following a certain file pattern.
        
        The file pattern depends on the workflow manager and follows usually the same as the generator.
        the list of paths is sorted alphabetically.
        """
        collector_files = []
        pattern = self.get_collector_pattern(info[Keys.COLLECTOR])
        collector_files.extend(glob.glob(pattern))
        collector_files.sort()
        return collector_files

    def get_collector_pattern(self, filename):
        """
        Return a search pattern based on a filename. 
        """
        return "%s_[0-9]*" % filename

    def main(self, info, log):
        """
        Merge collector files into a single dictionary.
        
        The values of the collector files are flattened. That means if a key value is equal across all
        collector files, the value is kept as single value. If values for the same key differ, a list of
        these values is created.      
        
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
        """
        #warn printing if user might have forgotten to set --INPUT collectfile_0 or cmdline arguments
        if not Keys.INPUT in info:
            log.warn("With Collector the keys BASEDIR, JOB_IDX, LOG_LEVEL and STORAGE "
                     "are changed to default if not set on commandline or in inputinfo. "
                     "To ensure consistency in the workflow it is recommended to set --INPUT collectfile_0")

        #Collect infos into one large collector_config object
        collector_config = {}
        paths = self.get_collector_files(info)
        if len(paths) == 0:
            log.critical('no collector files found [%s]' % paths)
            return 1, info
        for path in paths:
            log.debug('collecting ini file [%s]' % path)
            config = IniInformationHandler().get_info(log, {Keys.INPUT: path})
            collector_config = DictUtils.merge(log, collector_config, config, priority='append')

        #remove any keys that might interfere with runner keys afterwards
        for key in [Keys.BASEDIR, Keys.JOB_IDX, Keys.LOG_LEVEL, Keys.STORAGE]:
            log.info("Removing key %s from collector_info to ensure usage of value from INPUT" % key)
            if key in collector_config:
                del collector_config[key]

        #CHECKSUM
        if not collector_config.has_key(Keys.GENERATOR_CHECKSUM):
            log.warn("No checksum found, skipping check")
        else:
            if isinstance(collector_config[Keys.GENERATOR_CHECKSUM], list):
                log.debug("Converting checksum list to int for checking")
                collector_config[Keys.GENERATOR_CHECKSUM] = collector_config[Keys.GENERATOR_CHECKSUM][0]
            checksum = int(collector_config[Keys.GENERATOR_CHECKSUM])
            if checksum == len(paths):
                log.info("Checksum %d fits" % checksum)
            else:
                log.critical("Checksum %d and number of collected files %d do not match!" % (checksum, len(paths)))
                return 2, info

        log.debug('collected info content [%s]' % collector_config)
        return 0, collector_config

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.COLLECTOR,
                                  'Base name for collecting output files (e.g. from a parameter sweep)')

        args_handler.add_app_args(log, Keys.INPUT, 'for checking')
        #TODO: simplify "wholeinfo" apps
        args_handler.add_app_args(log, Keys.BASEDIR, 'get basedir if set or modified by runner')
        args_handler.add_app_args(log, Keys.JOB_IDX, 'get jobidx if set or modified by runner')
        args_handler.add_app_args(log, Keys.STORAGE, 'get storage if set or modified by runner')
        args_handler.add_app_args(log, Keys.LOG_LEVEL, 'get loglevel if set or modified by runner')
        return args_handler
        
    


    
