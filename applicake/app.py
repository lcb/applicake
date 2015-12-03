import os
import subprocess
import sys
import time
import getpass

from applicake.apputils import dirs
from applicake.apputils import dicts
from applicake.apputils import validation
from applicake.coreutils.keys import Keys, KeyHelp
from applicake.coreutils.log import Logger
from applicake.coreutils.arguments import Argument, parse_sysargs
from applicake.coreutils.info import get_handler


class IApp(object):
    @classmethod
    def main(cls):
        """
        Main method to run through the whole App

        @return : None
        """
        raise NotImplementedError

    def add_args(self):
        """
        Defines Arguments required or used by App

        @return: list with Arguments
        """
        raise NotImplementedError

    def setup(self, app_args):
        """
        Set up environment for running App

        @param app_args: Arguments required by App
        @return: logger, dict with info
        """
        raise NotImplementedError

    def run(self, log, info):
        """
        Run the App

        @param log: logger
        @param info: dict with info
        @return: (modified) dict with info
        """
        raise NotImplementedError

    def teardown(self, log, info):
        """
        Clean up enviroment after running App

        @param log: logger
        @param info: dict with info
        @return: None
        """
        raise NotImplementedError


class BasicApp(IApp):
    @classmethod
    def main(cls):
        log = None
        try:
            start = time.time()
            ci = cls()
            app_args = ci.add_args()
            log, req_info, info = ci.setup(app_args)
            ret_info = ci.run(log, req_info)
            info = dicts.merge(info, ret_info, priority='right')
            ci.teardown(log, info)
            log.debug("%s finished sucessfully at %s" % (cls.__name__, time.asctime()))
            log.info("%s finished sucessfully after %ss" % (cls.__name__, int(time.time() - start)))
        except Exception, e:
            msg = cls.__name__ + " failed! " + str(e)
            if isinstance(e, KeyError):
                msg += " key not found in info"
            msg += "\n"
            #feature request cuklinaj: mail when fail
            if os.environ.get("LSB_JOBID"):
                subprocess.call("echo \"Failure reason: %s\" | mail -s \"Workflow Failed\" %s" % (msg, getpass.getuser()) ,shell=True)
            # if app fails before logger is created use sys.exit for message
            if not log:
                sys.exit(msg)
            log.error(msg)
            sys.exit(1)

    def add_args(self):
        raise NotImplementedError("add_args() not implemented")

    def setup(self, app_args):
        # basic arguments for every node
        basic_args = [Argument(Keys.INPUT, KeyHelp.INPUT, default=''),
                      Argument(Keys.OUTPUT, KeyHelp.OUTPUT, default=''),
                      Argument(Keys.MODULE, KeyHelp.MODULE, default=''),
                      Argument(Keys.LOG_LEVEL, KeyHelp.LOG_LEVEL, default="DEBUG")]

        # Fixme: Prettify WORKDIR creation system
        # WORKDIR: if WORKDIR is defined add related args
        for i, arg in enumerate(app_args):
            if arg.name == Keys.WORKDIR:
                app_args.insert(i + 1, Argument(Keys.BASEDIR, KeyHelp.BASEDIR, default='.'))
                app_args.insert(i + 2, Argument(Keys.JOB_ID, KeyHelp.JOB_ID, default=''))
                app_args.insert(i + 3, Argument(Keys.SUBJOBLIST, KeyHelp.SUBJOBLIST, default=''))
                app_args.insert(i + 4, Argument(Keys.NAME, KeyHelp.NAME, default=self.__class__.__name__))
                break

        defaults, cliargs = parse_sysargs(basic_args + app_args)

        # construct info from defaults < info < commandlineargs
        ih = get_handler(cliargs.get(Keys.INPUT, None))
        fileinfo = ih.read(cliargs.get(Keys.INPUT, None))
        info = dicts.merge(cliargs, dicts.merge(fileinfo, defaults))

        # setup logging
        log = Logger.create(info[Keys.LOG_LEVEL])

        # request by malars: show dataset prominent in logger
        if Keys.DATASET_CODE in info:
            if not isinstance(info[Keys.DATASET_CODE], list):
                if Keys.MZXML in info and not isinstance(info[Keys.MZXML], list):
                    log.info("Dataset is %s (%s)" % (info[Keys.DATASET_CODE], os.path.basename(info[Keys.MZXML])))
                else:
                    log.info("Dataset is %s" % info[Keys.DATASET_CODE])
            else:
                log.debug("Datasets are %s" % info[Keys.DATASET_CODE])


        # WORKDIR: create WORKDIR (only after mk log)
        info = dirs.create_workdir(log, info)

        # filter to requested args
        if Keys.ALL_ARGS in info:
            # if ALL_ARGS is set give whole info to app...
            req_info = info
        else:
            req_info = {}
            # ...otherwise copy only explicitly requested args to app
            for key in [arg.name for arg in basic_args + app_args]:
                if key in info:
                    req_info[key] = info[key]
        log.debug("info for app: %s" % req_info)
        return log, req_info, info

    def run(self, log, info):
        raise NotImplementedError("run() not implemented")

    def teardown(self, log, info):
        ih = get_handler(info.get(Keys.OUTPUT))
        ih.write(info, info.get(Keys.OUTPUT))


class WrappedApp(BasicApp):
    def run(self, log, info):
        info, cmd = self.prepare_run(log, info)
        exit_code, stdout = self.execute_run(log, info, cmd)
        info = self.validate_run(log, info, exit_code, stdout)
        return info

    def prepare_run(self, log, info):
        raise NotImplementedError("prepare_run() not implemented")

    def execute_run(self, log, info, cmd):
        out = ""
        exit_code = 0
        if isinstance(cmd, list):
            for single_command in cmd:
                exit_code_s, out_s = self.execute_run_single(log, info, single_command)
                exit_code += exit_code
                out += out_s
                if exit_code_s !=0:
                    break
        else:
            exit_code, out = self.execute_run_single(log, info, cmd)
        return exit_code, out

    @staticmethod
    def execute_run_single(log, info, cmd):
        # Fixme: Prettify/document MODULE load system
        # if MODULE is set load specific module before running cmd. requires http://modules.sourceforge.net/
        if info.get('MODULE', '') != '':
            cmd = "module purge && module load %s && %s" % (info['MODULE'], cmd)

        cmd = cmd.replace("\n", "")
        log.debug("command is [%s]" % cmd)
        # stderr to stdout: http://docs.python.org/2/library/subprocess.html#subprocess.STDOUT
        # read input "streaming" from subprocess: http://stackoverflow.com/a/17698359
        # get exitcode: http://docs.python.org/2/library/subprocess.html#subprocess.Popen.returncode
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
        out = ""
        for line in iter(p.stdout.readline, ''):
            print line.strip()
            out += line
        p.communicate()
        exit_code = p.returncode
        return exit_code, out

    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_stdout(log, stdout)
        return info
