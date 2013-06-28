'''
Created on Mar 6, 2012

@author: quandtan
'''

import os
import random
import shutil
import string
import sys
import unittest
from cStringIO import StringIO
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication, IWrapper
from applicake.framework.runner import IniApplicationRunner, IniWrapperRunner


class Application(IApplication):
    out_txt = 'my stdout txt'
    log_txt = 'LOG'

    def main(self, info, log):
        print self.out_txt
        log.debug(self.log_txt)
        return 0, info

    def set_args(self, log, args_handler):
        return args_handler


class StorageBug(IApplication):
    def main(self, info, log):
        print info['STORAGE']
        return 0, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, 'STORAGE', 'storage')
        return args_handler


class Wrapper(IWrapper):
    out_txt = 'wrapper stdout text'
    log_txt = 'LOG'

    def prepare_run(self, info, log):
        log.debug(self.log_txt)
        prefix = info[Keys.PREFIX]
        command = '%s "%s"' % (prefix, self.out_txt)
        return command, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the Echo executable')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            exit_code = run_code
        else:
            exit_code = 0
        return exit_code, info


class Test(unittest.TestCase):
    def setUp(self):
        # if the log name is not different for all tests, there is a mix-up of messages
        self.random_name = ''.join(random.sample(string.ascii_uppercase + string.digits, 20))
        #create temporary files
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        self.input_ini = '%s/input.ini' % self.tmp_dir
        f = open(self.input_ini, 'w+')
        f.write("""COMMENT=test message
        STORAGE = impossible
        LOG_LEVEL = DEBUG
        OUTPUT = output.ini
        JOB_IDX = jobidx
        BASEDIR = %s""" % self.tmp_dir)
        f.close()
        self.output_ini = '%s/output.ini' % self.tmp_dir

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_iapplication__1(self):
        '''Test basic execution of emtpty app'''
        self.argv = []
        runner = IniApplicationRunner()
        application = Application()
        exitcode = runner(self.argv, application)
        assert exitcode == 0

    def test_iapplication__2(self):
        '''Test -i and -o'''
        stdoutstream = StringIO()
        sys.stdout = stdoutstream
        self.argv = ['-i', self.input_ini,
                     '-o', self.output_ini,
                     '-n', self.random_name]
        runner = IniApplicationRunner()
        application = Application()
        exitcode = runner(self.argv, application)

        assert os.path.exists(self.output_ini)
        assert os.path.getsize(self.output_ini) > 1
        assert exitcode == 0


    def test_iapplication__3(self):
        '''Test -s file, implicit JOBDIX/NAME/ folder creation'''
        self.argv = ['-i', self.input_ini,
                     '-o', self.output_ini,
                     '-n', 'AppName', '-s', 'file', '-l', 'DEBUG']
        runner = IniApplicationRunner()
        application = Application()
        exitcode = runner(self.argv, application)
        assert exitcode == 0
        logfile = self.tmp_dir + '/jobidx/AppName/AppName.log'
        assert os.path.exists(logfile)

    def test_iapplication_bug1(self):
        '''Bug in storage: if info has impossible value no exception is thrown'''
        self.argv = ['-i', self.input_ini,
                     '-o', self.output_ini]
        runner = IniApplicationRunner()
        application = StorageBug()
        exitcode = runner(self.argv, application)
        assert exitcode == 0

        self.argv = ['-i', self.input_ini,
                     '-o', self.output_ini, '-s', 'impossiblee']
        runner = IniApplicationRunner()
        application = StorageBug()
        exception = False
        try:
            runner(self.argv, application)
        except:
            exception = True
        self.assertTrue(exception, 'Should throw an expection')


    def test__iwrapper__1(self):
        '''Test of wrapper by reading comment from stdout '''
        self.argv = ['-i', self.input_ini,
                     '-o', self.output_ini, '--PREFIX', 'echo']

        stdout = StringIO()
        sys.stdout = stdout
        runner = IniWrapperRunner()
        wrapper = Wrapper()
        exit_code = runner(self.argv, wrapper)
        assert exit_code == 0

        sys.stdout = sys.__stdout__
        stdout.seek(0)
        #should contain: ===stdout === \n wrapper stdout text \n === stderr ==
        assert wrapper.out_txt in stdout.read()


if __name__ == "__main__":
    unittest.main()
