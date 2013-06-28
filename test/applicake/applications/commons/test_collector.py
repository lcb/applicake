'''
Created on Apr 18, 2012

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
from applicake.framework.runner import *
from applicake.applications.commons.collector import IniCollector


class Test(unittest.TestCase):
    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG', name='memory_logger', stream=log_stream)

        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)

        self.output = 'output.ini'

        self.collector_file = 'collector.ini'
        self.range = range(0, 10)
        a = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        b = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10']
        c = ['s1', 's1', 's1', 's2', 's2', 's2', 's3', 's3', 's3', 's10']
        for idx in range(0, 10):
            path = '_'.join([self.collector_file, "%s" % idx])
            x = a[idx]
            y = b[idx]
            z = c[idx]
            fh = open(path, 'w+')
            fh.write("""COMMENT = 'hello','world'
    STORAGE = memory
    GENERATOR_CHECKSUM = %s
    LOG_LEVEL = DEBUG
    BASEDIR = %s
    JOB_IDX = 15
    DATASET_CODE = 20120320164249179-361885,20120320164249179-361886,20120320164249179-361887
    COLLECTOR_IDX = %s
    P1 = %s
    P2 = %s
    P3 = %s
""" % (len(self.range), self.tmp_dir, idx, x, y, z))
            fh.close()


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_guse_collector_1(self):
        ''' Test with only collector and output flag, LOG_LEVEL and STORAGE are reset to default, BASEDIR and JOBIDX removed'''
        runner = IniApplicationRunner()
        app = IniCollector()
        sys.argv = ['--%s' % Keys.COLLECTOR, self.collector_file, '-o', self.output]
        exit_code = runner(sys.argv, app)
        assert exit_code == 0

        dic = dict(ConfigObj(self.output))
        expected = {
            Keys.COMMENT: [
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world'
            ],
            Keys.DATASET_CODE: [
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887'
            ],
            Keys.COLLECTOR_IDX: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            'P1': ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1'],
            'P2': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10'],
            'P3': ['s1', 's1', 's1', 's2', 's2', 's2', 's3', 's3', 's3', 's10'],
            Keys.STORAGE: "memory",
            Keys.GENERATOR_CHECKSUM: "10",
            Keys.LOG_LEVEL: "DEBUG",
        }

        # needed to print the diff
        self.assertDictEqual(expected, dic)

    def test_guse_collector_2(self):
        ''' Test with collector, output flag and other cmdline flags to override. STORAGE and LOG_LEVEL should be kept, BASEDIR and JOBIDX removed'''
        runner = IniApplicationRunner()
        wrapper = IniCollector()
        sys.argv = ['--%s' % Keys.COLLECTOR, self.collector_file, '-o', self.output, '-l', 'ERROR', '-s',
                    'file'] # for BasicArgsHandler()
        exit_code = runner(sys.argv, wrapper)
        assert 0 == exit_code

        dic = dict(ConfigObj(self.output))
        expected = {
            Keys.COMMENT: [
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world'
            ],
            Keys.DATASET_CODE: [
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887'
            ],
            'COLLECTOR_IDX': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            'P1': ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1'],
            'P2': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10'],
            'P3': ['s1', 's1', 's1', 's2', 's2', 's2', 's3', 's3', 's3', 's10'],
            Keys.JOB_IDX: ".",
            Keys.GENERATOR_CHECKSUM: "10",
            Keys.STORAGE: "file",
            Keys.LOG_LEVEL: "ERROR",
            Keys.BASEDIR: "."
        }

        self.assertDictEqual(expected, dic)

    def test_guse_collector_3(self):
        ''' Test with input, collector, output flag. STORAGE LOG_LEVEL BASEDIR and JOBIDX should all be kept'''
        runner2 = IniApplicationRunner()
        wrapper2 = IniCollector()
        sys.argv = ['--%s' % Keys.COLLECTOR, self.collector_file, '-o', self.output, '-i',
                    self.collector_file + "_0"] # for BasicArgsHandler()
        exit_code = runner2(sys.argv, wrapper2)
        assert 0 == exit_code

        dic = dict(ConfigObj(self.output))
        expected = {
            Keys.COMMENT: [
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world',
                'hello', 'world'
            ],
            Keys.DATASET_CODE: [
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887',
                '20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887'
            ],
            'COLLECTOR_IDX': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            'P1': ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1'],
            'P2': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10'],
            'P3': ['s1', 's1', 's1', 's2', 's2', 's2', 's3', 's3', 's3', 's10'],
            Keys.JOB_IDX: "15",
            Keys.GENERATOR_CHECKSUM: "10",
            Keys.STORAGE: "memory",
            Keys.LOG_LEVEL: "DEBUG",
            Keys.BASEDIR: self.tmp_dir
        }

        self.assertDictEqual(expected, dic)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_guse_collector']
    unittest.main()
