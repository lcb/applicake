"""
Created on Jun 6, 2012

@author: quandtan
"""

import os
import sys
from applicake.framework.keys import Keys
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator
from applicake.framework.interfaces import IWrapper


class InterProphet(IWrapper):
    """
    Wrapper for the TPP-tool InterProphetParser.
    """

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.pep.xml' % base # result produced by the application

    def get_prefix(self, info, log):
        if not info.has_key(Keys.PREFIX):
            info[Keys.PREFIX] = 'InterProphetParser'
            log.debug('set [%s] to [%s] because it was not set before.' % (Keys.PREFIX, info[Keys.PREFIX]))
        return info[Keys.PREFIX], info

    def prepare_run(self, info, log):
        """
        See interface.
        """
        wd = info[Keys.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._result_file = os.path.join(wd, self._result_file)
        if not isinstance(info[Keys.PEPXMLS], list):
            info[Keys.PEPXMLS] = [info[Keys.PEPXMLS]]
        old = info[Keys.PEPXMLS]
        # this check has to be included to cope with non-failing workflow engines
        for path in old:
            if not FileUtils.is_valid_file(log, path):
                log.fatal('Input file [%s] is not valid' % path)
                sys.exit(1)
        new = self._result_file
        log.debug('replace value of [%s] [%s] with [%s]' % (Keys.PEPXMLS, old, new))
        info[Keys.PEPXMLS] = [new]
        prefix, info = self.get_prefix(info, log)
        command = '%s %s %s %s' % (prefix, info['IPROPHET_ARGS'], ' '.join(old), new)
        return command, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PEPXMLS, 'List of pepXML files', action='append')
        args_handler.add_app_args(log, 'IPROPHET_ARGS', 'Arguments for InterProphetParser',default='MINPROB=0')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.

        Check the following:
        -
        """
        if 0 != run_code:
            return run_code, info
        err_stream.seek(0)
        for line in err_stream.readlines():
            if 'fin: error opening' in line:
                log.error("could not read the input file [%s]" % line)
                return 1, info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1, info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1, info
        return 0, info
