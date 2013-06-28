'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys

from configobj import ConfigObj

from applicake.framework.runner import IniApplicationRunner
from applicake.applications.commons.unifier import IniUnifier


class Test(unittest.TestCase):
    def setUp(self):
        self.input = 'echo_test.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        fh = open(self.input, 'w+')
        fh.write("""STORAGE = file
LOG_LEVEL = INFO
JOB_IDX = jobidx
FILE_IDX = 0,1,2,0,1,2
FILES = F0,F1,F2,F0,F1,F2
PARAM_IDX = 0,0,0,1,1,1
PARAM = p,p,p,a,a,a
THIRD = third
FOUR = some,thing,very,wild
BASEDIR = %s""" % self.tmp_dir)
        fh.close()
        self.output = 'output.ini'
        self.generate = "generate.ini"

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_unifier__1(self):
        runner = IniApplicationRunner()
        app = IniUnifier()
        sys.argv = ['-i', self.input, '-o', self.output]
        exit_code = runner(sys.argv, app)
        assert 0 == exit_code
        expected = {'FILES': ['F0', 'F1', 'F2'],
                    'LOG_LEVEL': 'INFO',
                    'PARAM_IDX': ['0', '1'],
                    'BASEDIR': self.tmp_dir,
                    'STORAGE': 'file',
                    'PARAM': ['p', 'a'],
                    'FOUR': ['some', 'thing', 'very', 'wild'],
                    'THIRD': 'third',
                    'FILE_IDX': ['0', '1', '2'],
                    'JOB_IDX': 'jobidx'}
        actual = ConfigObj(self.output)
        self.assertDictEqual(expected, actual)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_run_guse_generator']
    unittest.main()
