"""
Created on Apr 17, 2012

@author: quandtan
"""

import sys

from configobj import ConfigObj

from applicake.framework.keys import Keys

from applicake.framework.interfaces import IInformationHandler
from applicake.utils.dictutils import DictUtils
from applicake.utils.fileutils import FileUtils


class IniInformationHandler(IInformationHandler):
    """    
    Basic implementation (INI) of the IInformationHandler interface. 
    """

    def __init__(self):
        # keys that have to be removed before writing the information object
        self.remove_keys = [Keys.INPUT, Keys.OUTPUT, Keys.GENERATOR, Keys.COLLECTOR, Keys.NAME, Keys.PREFIX,
                            Keys.TEMPLATE, Keys.WORKDIR]

    def get_info(self, log, pargs):
        """
        See super class.
        
        Command line arguments and arguments in the input file(s) are merged.
        Priority is on the command line arguments.
        Input files are identified by INPUT
        If there are multiple input files, they are merged first by creating value lists.
        If there are no input files pargs is returned.  
        """

        pargs = pargs.copy()
        if not pargs.has_key(Keys.INPUT):
            log.debug('content of pargs [%s]' % pargs)
            log.info('pargs did not contain the key [%s]. Therefore no info is read.' % Keys.INPUT)
            return pargs
        else:
            path = pargs[Keys.INPUT]
            if not FileUtils.is_valid_file(log, path):
                log.fatal('Exit program because inputfile [%s] is not valid' % path)
                sys.exit(1)

            config = ConfigObj(path)
            return config

    def write_info(self, info, log):
        """
        See super class 
        
        Info is written to a single file that is following the Windows INI format. 
        """
        if info.has_key(Keys.OUTPUT):
            path = info[Keys.OUTPUT]
            log.debug('output file [%s]' % path)
            info_write = DictUtils.extract(info, self.remove_keys, include=False)
            log.debug('removed following keys [%s] before writing info' % self.remove_keys)
            config = ConfigObj(info_write)
            config.filename = path
            config.write()
            valid = FileUtils.is_valid_file(log, path)
            if not valid:
                log.fatal('Exit program because output file [%s] was not valid' % path)
                sys.exit(1)
        else:
            log.info('info object did not contain key [%s]. Therefore no info is written' % Keys.OUTPUT)                                                                                                                                    
                                        
