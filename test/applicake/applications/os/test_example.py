'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
from applicake.framework.runner import IniWrapperRunner, IniApplicationRunner
from applicake.applications.os.example import ExampleApplication, ExampleWrapper, ExampleTemplateApplication


class Test(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        self.input = 'input.ini'
        fh = open(self.input, 'w+')
        fh.write("""COMMANDOUTFILE = cmof
PREFIX = date
JOB_IDX = jobidx
BASEDIR = %s""" % self.tmp_dir)
        fh.close()
        self.output = 'output.ini'

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)

    def test_exampleapp(self):
        runner = IniApplicationRunner()
        wrapper = ExampleApplication()
        sys.argv = ['-i', self.input, '-o', self.output, '--COMMENT', 'hello world']
        exit_code = runner(sys.argv, wrapper)
        assert 0 == exit_code

    def test_exampletemplateapp(self):
        runner = IniApplicationRunner()
        wrapper = ExampleTemplateApplication()
        sys.argv = ['-i', self.input, '-o', self.output, '-s', 'file', "--COMMENT", "ToBeInserted", "-n", "name"]
        exit_code = runner(sys.argv, wrapper)
        assert 0 == exit_code
        assert "A template string for [ToBeInserted]" == open(self.tmp_dir + '/jobidx/name/test.tpl').read().strip()

    def test_examplewrapper(self):
        runner = IniWrapperRunner()
        wrapper = ExampleWrapper()
        sys.argv = ['-i', self.input, '-o', self.output]
        exit_code = runner(sys.argv, wrapper)
        assert 0 == exit_code
        assert os.path.exists('cmof')


if __name__ == "__main__":
    unittest.main()
