#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: quandtan
"""

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper


class Echo(IWrapper):
    """
    Performs echo of an of the argument comment
    """

    def prepare_run(self, info, log):
        try:
            comment = info[Keys.COMMENT]
            prefix = info[Keys.PREFIX]
        except:
            log.fatal('did not find one of the keys [%s %s]' % (Keys.COMMENT, Keys.PREFIX))
            return 'false', info
        return '%s "%s"' % (prefix, comment), info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.COMMENT, 'Descriptive sentence')
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the Echo executable', default="/bin/echo")
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info

        out_stream.seek(0)
        out = out_stream.read()
        if len(out) == 0:
            log.error('The output stream did not contain any value. check if key [COMMENT] was set')
            return 1, info

        return run_code, info
