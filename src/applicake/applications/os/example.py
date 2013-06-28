#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: loblum
"""

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper, IApplication
from applicake.utils.fileutils import FileUtils
from applicake.framework.templatehandler import BasicTemplateHandler


class ExampleApplication(IApplication):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.COMMENT, 'comment to log')
        return args_handler

    def main(self, info, log):
        print "Printing something [%s]" % info[Keys.COMMENT]
        log.info("Logging something [%s]" % info[Keys.COMMENT])
        return 0, info


class ExampleTemplateApplication(IApplication):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.COMMENT, 'comment to log')
        args_handler.add_app_args(log, Keys.WORKDIR, 'working directory created by runner')

        return args_handler

    def main(self, info, log):
        th = BasicTemplateHandler()
        template = "A template string for [$COMMENT]"
        mod_template, info = th.modify_template(info, log, template)

        templatefile = info[Keys.WORKDIR] + 'test.tpl'
        open(templatefile, "w").write(template)
        info[Keys.TEMPLATE] = templatefile
        mod_templatefile, info = th.modify_template(info, log)
        print mod_template, mod_templatefile

        return 0, info


class ExampleWrapper(IWrapper):
    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'executable to run', default="/bin/date")
        args_handler.add_app_args(log, "COMMANDOUTFILE", 'output of the executable goes here')
        return args_handler

    def prepare_run(self, info, log):
        command = "%s > %s" % (info["PREFIX"], info["COMMANDOUTFILE"])
        return command, info

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info
        outfile = info["COMMANDOUTFILE"]
        if not FileUtils.is_valid_file(log, outfile):
            return 1, info
        #if not XmlValidator.is_wellformed(outfile):
        #    return 1, info
        return 0, info

