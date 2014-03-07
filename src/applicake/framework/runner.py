#!/bin/env python

"""
Created on May 11, 2013

@author: quandtan, loblum
"""

import os
import shutil
import sys
import time
import tempfile
import errno
import subprocess
from cStringIO import StringIO
from applicake.framework.argshandler import ArgsHandler
from applicake.framework.keys import Keys
from applicake.framework.logger import Logger
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.framework.informationhandler import IniInformationHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.dictutils import DictUtils


class Runner(object):
    """
    Basic class to prepare and run one of the Interface classes of the framework as workflow node    
    """

    def __call__(self, args, app):
        """
        Run the specified app using the info set in the args.    
               
        @param args: From somewhere the runner needs to know where to find the info (file, url). this is extracted 
        @param app: the IApplication object to be run  
        
        @return int: exit code (0 for success)      
        """
        #init
        init_info = {Keys.NAME: app.__class__.__name__,
                     Keys.STORAGE: "memory",
                     Keys.LOG_LEVEL: "DEBUG"}
        init_log_stream = StringIO()
        init_log = Logger.create(level=init_info[Keys.LOG_LEVEL], stream=init_log_stream)

        #parse command line arguments
        args_handler = ArgsHandler()
        args_handler = self.set_args(args_handler) #runner args
        args_handler = app.set_args(init_log, args_handler) #application args
        parsed_args, default_args = args_handler.get_parsed_arguments(init_log, args)

        #parse info object
        info_handler = self.get_info_handler()
        parsed_info = info_handler.get_info(init_log, dict(parsed_args.items() + default_args.items()))

        #merge infos to final init_info < default args < info < args
        info = init_info
        info = DictUtils.merge(init_log, default_args, info, priority='left')
        info = DictUtils.merge(init_log, parsed_info, info, priority='left')
        info = DictUtils.merge(init_log, parsed_args, info, priority='left')

        #setup environment
        info = self._create_workdir(init_log, info) #basedir jobidx paramidx fileidx name
        out_stream, err_stream, log_stream = self._create_streams(info) #workdir storage      
        log = self._create_logger(info, init_log_stream, log_stream) #loglevel name

        log.debug("Info before running app: %s" % info)
        exit_code, info = self.run_app(app, info, log, args_handler, out_stream, err_stream)
        if exit_code != 0:
            log.error('Exit code was [%d], something went wrong above!'%exit_code)
            self._flush_logs(info, out_stream, err_stream, log_stream)
            return exit_code

        #cleanup
        info_handler.write_info(info, log)
        self._copy_infos_to_workdir(info, log) #input output
        self._flush_logs(info, out_stream, err_stream, log_stream)
        return exit_code

    def _create_workdir(self, log, info):
        if info[Keys.STORAGE] == 'memory':
            log.debug("Memory storage, not creating workdir")
            return info

        if not Keys.BASEDIR in info:
            log.warn("BASEDIR key not found, setting BASEDIR and JOBIDX to current folder!")
            info[Keys.BASEDIR] = "."
            info[Keys.JOB_IDX] = "."
        if not Keys.JOB_IDX in info:
            info[Keys.JOB_IDX] = self._create_unique_jobdir(info[Keys.BASEDIR])
            log.info("set JOB_IDX = %s"%info[Keys.JOB_IDX])

        info[Keys.WORKDIR] = ''
        for key in [Keys.BASEDIR, Keys.JOB_IDX, Keys.PARAM_IDX, Keys.FILE_IDX, Keys.NAME]:
            if key in info:
                if not isinstance(info[key], list):
                    info[Keys.WORKDIR] += info[key] + os.path.sep
                else:
                    #happens with runs after collector
                    log.debug("Key %s is a list, thus not used for creating workdir" % key)

        FileUtils.makedirs_safe(log, info[Keys.WORKDIR], clean=True)
        log.debug("Created workdir [%s]" % info[Keys.WORKDIR])
        return info
        
    def _create_unique_jobdir(self, basedir):
        #taken from tempfile.mkdtemp(), more compact. limit: no more than 10'000 WF submission per day!
        dirname = time.strftime("%y%m%d%H%M")
        for seq in xrange(10000):
            try: 
                os.mkdir(os.path.join(basedir,dirname), 0775)
                return dirname
            except OSError, e:
                if e.errno == errno.EEXIST:
                    dirname = str(int(dirname) + 1)
                    continue # try again
                raise
        raise Exception("Could not create a unique job directory")   

    def _create_streams(self, info):
        if info[Keys.STORAGE] == 'file':
            base = os.path.join(info[Keys.WORKDIR], info[Keys.NAME])
            out_stream = open(base + ".out", 'w+', buffering=0)
            err_stream = open(base + ".err", 'w+', buffering=0)
            log_stream = open(base + ".log", 'w+', buffering=0)
        else:
            out_stream = StringIO()
            err_stream = StringIO()
            log_stream = sys.stderr

        return out_stream, err_stream, log_stream

    def _create_logger(self, info, init_log_stream, log_stream):
        #only copy >= LOG_LEVEL entries from init_log. ' - ' is little patch if INFO is somewhere else in line
        init_log_stream.seek(0)
        for line in init_log_stream.readlines():
            for level in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
                if ' - ' + level + ' - ' in line:
                    log_stream.write(line)
                if level == info[Keys.LOG_LEVEL]:
                    break

        log = Logger.create(level=info[Keys.LOG_LEVEL], name=info[Keys.NAME], stream=log_stream)
        log.debug("Created logger with level %s" % info[Keys.LOG_LEVEL])
        return log

    def _copy_infos_to_workdir(self, info, log):
        if info[Keys.STORAGE] == 'memory':
            log.debug("Memory storage, not copying infos to workdir")
            return

        for key in [Keys.INPUT, Keys.OUTPUT]:
            if not key in info:
                continue
            try:
                log.debug("Copying info %s to %s" % (info[key], info[Keys.WORKDIR]))
                shutil.copy(info[key], info[Keys.WORKDIR])
            except:
                log.error("Could not copy [%s] to [%s]" % (info[key], info[Keys.WORKDIR]))

    def _flush_logs(self, info, out_stream, err_stream, log_stream):
        if info[Keys.STORAGE] == 'file':
            out_stream.close()
            err_stream.close()
            log_stream.close()
        else:
            #STORAGE=memory/unchgd: log stream already in stderr
            print '=== stdout ==='
            out_stream.seek(0)
            print out_stream.read()
            out_stream.close()
            print '=== stderr ==='
            err_stream.seek(0)
            print err_stream.read()
            err_stream.close()


    def get_info_handler(self):
        """
        Define which information handler to use (e.g. INI/CTD). 
        @return IInformation: An implementation of the IInformation interface. 
        """
        raise NotImplementedError("get_info_handler() is not implemented.")

    def run_app(self, app, info, log, args_handler, out_stream, err_stream):
        """
        Executes an object that implements the supported Application interface.        
        @return: Tuple of 2 objects; the exit code and the (updated) info object.
        """
        raise NotImplementedError("run_app() is not implemented.")

    def set_args(self, args_handler):
        """
        Define specific arguments needed by the runner (not same as app_args!)
        Note: use --collector if you have >1 input, --generator if >1 output!
        Overridden by IniWrapperRunner to set module
        """
        args_handler.add_runner_args('-i', '--INPUT', required=False, dest="INPUT", action='store',
                                     help="Input (configuration) file")
        args_handler.add_runner_args('-o', '--OUTPUT', required=False, dest="OUTPUT", action='store',
                                     help="Output (configuration) file")
        args_handler.add_runner_args('-n', '--NAME', required=False, dest="NAME", help="Name of the workflow node")
        args_handler.add_runner_args('-s', '--STORAGE', required=False, dest="STORAGE",
                                     choices=['memory', 'unchanged', 'file'], help="Storage type for out/err/log")
        args_handler.add_runner_args('-l', '--LOG_LEVEL', required=False, dest="LOG_LEVEL",
                                     choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        args_handler.add_runner_args('-d', '--BASEDIR', required=False, dest="BASEDIR",
                                     help="Base directory used to store files produced by the application")
        return args_handler


class IniApplicationRunner(Runner):
    """    
    Runner class that supports application that implement the IApplication interface (pure python apps).
    """

    def get_info_handler(self):
        return IniInformationHandler()

    def run_app(self, app, info, log, args_handler, out_stream, err_stream):
        if not isinstance(app, IApplication):
            log.critical('%s is not instance of IApplicataion' % app.__class__.__name__)
            return 1, info

        app_info = DictUtils.extract(info, args_handler.get_app_argnames())
        exit_code, app_info = app.main(app_info, log)
        info = DictUtils.merge(log, info, app_info, priority='right')
        #validate run not needed, should be done in app.main()
        return exit_code, info


class IniWrapperRunner(Runner):
    """
    Runner class that supports application that implement the IWrapper interface      
        
    The Application type is used to create workflow nodes that 
    prepare, run and validate the execution of an external application.
    """

    def set_args(self, args_handler):
        args_handler.add_runner_args('-m', '--MODULE', required=False, dest="MODULE", help="module to load.")
        return super(IniWrapperRunner, self).set_args(args_handler)

    def get_info_handler(self):
        return IniInformationHandler()

    def run_app(self, app, info, log, args_handler, out_stream, err_stream):
        """
        Prepare, run and validate the execution of an external program. 
        
        See super class.
        """
        if not isinstance(app, IWrapper):
            log.critical('%s is not instance of IWrapper' % app.__class__.__name__)
            return 1, info

        app_info = DictUtils.extract(info, args_handler.get_app_argnames())
        command, app_info = app.prepare_run(app_info, log)
        info = DictUtils.merge(log, info, app_info, priority='right')
        # necessary when e.g. the template file contains '\n' what will cause problems using shell=True
        log.debug('remove all newlines from command string')
        command = command.replace('\n', '')
        #MODULE LOAD
        if 'MODULE' in info:
            log.debug("Overriding module with " + info['MODULE'])
            command = "module purge && module load " + info['MODULE'] + " && " + command

        #http://stackoverflow.com/a/165662
        log.info("command is [ %s ]" % command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        out_stream.write(output)
        err_stream.write(error)
        run_code = p.returncode
        log.debug('run exit code [%s]' % run_code)

        out_stream.seek(0)
        err_stream.seek(0)
        validate_code, app_info = app.validate_run(app_info, log, run_code, out_stream, err_stream)
        log.debug('validation exit code [%s]' % validate_code)
        info = DictUtils.merge(log, info, app_info, priority='right')
        return validate_code, info

