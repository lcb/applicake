'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
import glob

from configobj import ConfigObj

from applicake.framework.keys import Keys
from applicake.framework.runner import IniApplicationRunner
from applicake.applications.commons.generator import IniDatasetcodeGenerator, IniParametersetGenerator
from applicake.applications.commons.collector import IniCollector


class Test(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = '%s/tmp/' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        fh = open('input.ini', 'w+')
        fh.write("""COMMENT = 'hello','world'
BASEDIR = %s
DATASET_CODE = 20120320164249179-11111,20120320164249179-22222,20120320164249179-33333
STORAGE = file
JOB_IDX = jobidx
LOG_LEVEL = INFO
""" % self.tmp_dir)
        fh.close()


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_GeneratorCollectUnify(self):
        '''test generator collector unify sequence'''
        runner = IniApplicationRunner()
        app = IniDatasetcodeGenerator()
        sys.argv = ['-i', 'input.ini', '--%s' % Keys.GENERATOR, 'generate.ini']
        exit_code = runner(sys.argv, app)
        assert 0 == exit_code
        assert 6 == len(glob.glob(self.tmp_dir + "generate.ini_*"))

        app = IniCollector()
        sys.argv = ['-i', 'generate.ini_0', '--%s' % Keys.COLLECTOR, 'generate.ini', '-o', 'collect.ini']
        exit_code = runner(sys.argv, app)
        assert exit_code == 0
        d1 = {'COMMENT': ['hello', 'hello', 'hello', 'world', 'world', 'world'],
              'DATASET_CODE': ['20120320164249179-11111', '20120320164249179-22222', '20120320164249179-33333',
                               '20120320164249179-11111', '20120320164249179-22222', '20120320164249179-33333'],
              'LOG_LEVEL': 'INFO',
              'PARAM_IDX': ['0', '0', '0', '1', '1', '1'],
              'GENERATOR_CHECKSUM': '6',
              'BASEDIR': self.tmp_dir,
              'STORAGE': 'file',
              'JOB_IDX': 'jobidx',
              'FILE_IDX': ['0', '1', '2', '0', '1', '2']}
        d2 = ConfigObj(self.tmp_dir + "collect.ini")
        self.assertDictEqual(d1, d2)

        app = IniParametersetGenerator()
        sys.argv = ['-i', 'collect.ini', '--GENERATOR', 'paramgen.ini']
        exit_code = runner(sys.argv, app)
        assert exit_code == 0
        assert 2 == len(glob.glob(self.tmp_dir + "/paramgen.ini_*"))
        actual = ConfigObj(self.tmp_dir + "/paramgen.ini_0")
        expected = {'COMMENT': 'hello',
                    'DATASET_CODE': ['20120320164249179-11111', '20120320164249179-22222', '20120320164249179-33333'],
                    'LOG_LEVEL': 'INFO',
                    'PARAM_IDX': '0',
                    'GENERATOR_CHECKSUM': '2',
                    'BASEDIR': self.tmp_dir,
                    'STORAGE': 'file',
                    'JOB_IDX': 'jobidx'}
        self.assertDictEqual(actual, expected)

        actual2 = ConfigObj(self.tmp_dir + "paramgen.ini_1")
        expected2 = {'COMMENT': 'world',
                     'DATASET_CODE': ['20120320164249179-11111', '20120320164249179-22222', '20120320164249179-33333'],
                     'LOG_LEVEL': 'INFO',
                     'PARAM_IDX': '1',
                     'GENERATOR_CHECKSUM': '2',
                     'BASEDIR': self.tmp_dir,
                     'STORAGE': 'file',
                     'JOB_IDX': 'jobidx'}
        self.assertDictEqual(actual2, expected2)


if __name__ == "__main__":
    unittest.main()
