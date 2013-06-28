'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
from StringIO import StringIO

from configobj import ConfigObj

from applicake.framework.keys import Keys
from applicake.framework.logger import Logger
from applicake.framework.runner import IniWrapperRunner
from applicake.applications.os.echo import Echo


class Test(unittest.TestCase):
    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG', name='memory_logger', stream=log_stream)
        self.input = 'echo_test.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        fh = open(self.input, 'w+')
        fh.write("""%s = hello world
%s = /bin/echo        
%s = file
%s = /fake/output.ini 
%s = INFO
JOB_IDX = jobindex
%s = %s
""" % (Keys.COMMENT, Keys.PREFIX, Keys.STORAGE, Keys.OUTPUT, Keys.LOG_LEVEL, Keys.BASEDIR, self.tmp_dir))
        fh.close()
        self.output = 'myoutput.ini'

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_prepare_run(self):
        org_info = {Keys.PREFIX: '/bin/echo', Keys.COMMENT: 'hello world'}
        comment, info = Echo().prepare_run(org_info, self.log)
        assert comment == '/bin/echo "hello world"'
        assert org_info == info


    def test_echo_1(self):
        """Test with input.ini"""
        runner = IniWrapperRunner()
        wrapper = Echo()
        sys.argv = ['-i', self.input, '-o', self.output, '--%s' % Keys.LOG_LEVEL, 'DEBUG', '-s', 'file']
        exit_code = runner(sys.argv, wrapper)
        assert 0 == exit_code

        config = ConfigObj(self.output)
        print config
        assert 'hello world\n' == open(self.tmp_dir + '/jobindex/Echo/Echo.out', 'r').read()
        assert os.path.getsize(self.tmp_dir + '/jobindex/Echo/Echo.err') == 0
        assert os.path.getsize(self.tmp_dir + '/jobindex/Echo/Echo.log') > 0

    def test_validate_run(self):
        app = Echo()
        out = StringIO()
        out.write("FOO")
        info = {}
        log = Logger.create()
        code, info = app.validate_run(info, log, 0, out, out)
        assert code == 0

        code, info = app.validate_run(info, log, 1, out, out)
        assert code == 1

        code, info = app.validate_run(info, log, 1, StringIO(), out)
        assert code == 1


if __name__ == "__main__":
    unittest.main()
