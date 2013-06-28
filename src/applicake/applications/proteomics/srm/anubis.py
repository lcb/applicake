#!/usr/bin/env python
"""
Created on Oct 3, 2012

@author: johant,quandtan
"""

import os
import re
import shlex
import subprocess

from applicake.framework.interfaces import IWrapper
from applicake.framework.keys import Keys
from applicake.utils.xmlutils import XmlValidator
from applicake.utils.fileutils import FileUtils


class AnubisException(Exception):
    def __init__(self, mess):
        self.mess = mess


class Anubis(IWrapper):
    """
    Runs anubis
    """

    NULL_DIST_SIZE = 'ANUBIS_NULL_DIST_SIZE'
    MAX_NUM_TRANSITIONS = 'ANUBIS_MAX_NUM_TRANSITIONS'
    PEAK_MIN_WIDTH = 'ANUBIS_PEAK_MIN_WIDTH'
    SINGLE_ANSWER = 'ANUBIS_SINGLE_ANSWER'
    P_VALUE_TOLERANCE = 'ANUBIS_P_VALUE_TOLERANCE'
    VERSION = 'ANUBIS_VERSION'
    JVM = 'ANUBIS_JVM'
    JVM_VERSION = 'ANUBIS_JVM_VERSION'
    MAX_HEAP_SIZE = 'ANUBIS_MAX_HEAP_SIZE'
    #    LOG_DIR             = 'ANUBIS_LOG_DIR'
    #    OUTPUT_RESULT_FILE  = 'ANUBIS_OUTPUT'
    TRAML = 'TRAML'

    DEFAULT_JVM = 'java'
    DEFAULT_ANUBIS_DIR = '.'
    #    DEFAULT_LOG_DIR     = './log'
    #    DEFAULT_ANUBIS_JAR  = '/media/storage/code/anubis_workspace/Anubis/target/Anubis-1.1.0-jar-with-dependencies.jar'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.anubis.xml' % base # result produced by the application
        self._log_dir = 'log' # dir where log files are stored

    def prepare_run(self, info, log):
        """
        See interface
        """

        def get(param, default):
            if param not in info:
                info[param] = default
            return info[param]

        def require(param):
            if param not in info:
                raise AnubisException('did not find the required %s key' % param)
            return info[param]

        def fatal(mess):
            log.fatal(mess)
            print mess
            return '', info


        try:
            cmd = get(self.JVM, self.DEFAULT_JVM)
            cmd += ' -Xmx%s -jar ' % get(self.MAX_HEAP_SIZE, '1g')

            if self.VERSION in info:
                cmd += "anubis-%s.jar " % info[self.VERSION]
            else:
                mess = ''
                try:
                    anubisCmd = cmd + self.DEFAULT_ANUBIS_DIR + "/anubis.jar"
                    p = subprocess.Popen(shlex.split(anubisCmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output = p.communicate()[0]
                    m = re.search('(?<=anubis-)[^ ]*(?=.jar)', output)
                    if m is not None:
                        info[self.VERSION] = m.group(0)
                        cmd += "%s/anubis.jar " % self.DEFAULT_ANUBIS_DIR
                    else:
                        mess = 'could not extract anubis version from %s/anubis.jar output' % self.DEFAULT_ANUBIS_DIR
                except:
                    mess = 'could not run %s/anubis.jar' % (cmd + self.DEFAULT_ANUBIS_DIR)
                finally:
                    try:
                        p = subprocess.Popen(shlex.split("rm -r log"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        _, _ = p.communicate()
                    except Exception, e:
                        log.warning("could not delete log directory after extracting anubis version: %s" % e)
                if mess != '':
                    return fatal(mess)

            wd = info[Keys.WORKDIR]
            self._result_file = os.path.join(wd, self._result_file)
            self._log_dir = os.path.join(wd, self._log_dir)

            cmd += "--null-dist=%i " % int(get(self.NULL_DIST_SIZE, 1000))
            cmd += "--trans-limit=%i " % int(get(self.MAX_NUM_TRANSITIONS, 6))
            cmd += "--single-answer=%s " % get(self.SINGLE_ANSWER, "true")
            cmd += "--p-value-tolerance=%f " % float(get(self.P_VALUE_TOLERANCE, 0.01))
            cmd += "--log-dir=%s " % self._log_dir
            cmd += '%s ' % require(Keys.TRAML)
            cmd += "%f " % float(get(self.PEAK_MIN_WIDTH, 0.1))
            cmd += '%s ' % self._result_file
            cmd += '%s' % require(Keys.MZML)

            return cmd, info

        except AnubisException, ae:
            return fatal(ae.mess)


    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.WORKDIR,
                                  'Directory to store files')

        args_handler.add_app_args(log, self.NULL_DIST_SIZE,
                                  'size of null distrubution for each chromatogram ( > 0, default: 1000)')

        args_handler.add_app_args(log, self.MAX_NUM_TRANSITIONS,
                                  'limit on the number of transitions used ( > 2, default: 6)')

        args_handler.add_app_args(log, self.SINGLE_ANSWER,
                                  'report only the best peak per chromatogram (largest within p-value-tolerance of best),' +
                                  ' instead of every peak within tolerance (false|true, default: true)')

        args_handler.add_app_args(log, self.P_VALUE_TOLERANCE,
                                  'p-value tolerance where peaks are considered equal (1.0 >= x >= 0.0, default: 0.01)')

        args_handler.add_app_args(log, self.PEAK_MIN_WIDTH,
                                  'minimum expected peak width in minutes ( > 0.0, default: 0.1)')

        args_handler.add_app_args(log, Keys.TRAML,
                                  'traml file with reference transition intensities')

        args_handler.add_app_args(log, self.VERSION,
                                  'anubis version to use (default: version of anubis.jar)')

        args_handler.add_app_args(log, self.JVM,
                                  'the jvm to use (default: java')

        args_handler.add_app_args(log, self.MAX_HEAP_SIZE,
                                  'jvm max heap size 124m = 124 Mb, 1g = 1 Gb (default: 1g)')

        #        args_handler.add_app_args(log, self.OUTPUT_RESULT_FILE,
        #            'the anubis result file')

        args_handler.add_app_args(log, Keys.MZML,
                                  'the MzML file to analyze')

        return args_handler


    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See interface
        """
        if run_code != 0:
            exit_code = run_code
        else:
            if not FileUtils.is_valid_file(log, self._result_file):
                log.critical('[%s] is not valid' % self._result_file)
                return 1, info
            if not XmlValidator.is_wellformed(self._result_file):
                log.critical('[%s] is not well formed.' % self._result_file)
                return 1, info
            exit_code = 0
        return exit_code, info
