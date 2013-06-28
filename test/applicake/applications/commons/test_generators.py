'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
import glob
from StringIO import StringIO

from applicake.framework.keys import Keys
from applicake.framework.logger import Logger
from applicake.framework.runner import IniApplicationRunner
from applicake.applications.commons.generator import IniDatasetcodeGenerator, IniParametersetGenerator


class Test(unittest.TestCase):
    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG', name='memory_logger', stream=log_stream)
        self.input = 'input.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        fh = open(self.input, 'w+')
        fh.write("""COMMENT = 'hello','world'
BASEDIR = %s
DATASET_CODE = 20120320164249179-11111,20120320164249179-22222,20120320164249179-33333
""" % self.tmp_dir)
        fh.close()

        fh = open('paraminput.ini', 'w+')
        fh.write("""COMMENT = C1,C1,C1,C2,C2,C2
BASEDIR = %s
DATASET_CODE = DS1,DS2,DS3,DS1,DS2,DS3
FILE_IDX = 0,1,2,0,1,2
PARAM_IDX = 0,0,0,1,1,1
""" % self.tmp_dir)
        fh.close()

        self.output = 'generate.ini'


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)

    def test_generator_1(self):
        '''test 3datasets x 2comments = 6generateini'''
        runner = IniApplicationRunner()
        app = IniDatasetcodeGenerator()
        sys.argv = ['-i', 'input.ini', '-o', 'output.ini', '--%s' % Keys.GENERATOR, self.output]
        exit_code = runner(sys.argv, app)
        assert 0 == exit_code
        assert 6 == len(glob.glob(self.tmp_dir + "/generate.ini_*"))
        assert "GENERATOR_CHECKSUM = 6" in open(self.tmp_dir + "/generate.ini_0").read()

    def test_generator_2(self):
        '''test 3ds x 2comments 0 2paramini'''
        runner = IniApplicationRunner()
        app = IniParametersetGenerator()
        sys.argv = ['-i', 'paraminput.ini', '-o', 'output.ini', '--%s' % Keys.GENERATOR, 'paramout.ini']
        exit_code = runner(sys.argv, app)
        assert 0 == exit_code
        assert 2 == len(glob.glob(self.tmp_dir + "/paramout.ini_*"))


    def test_generator_bug1(self):
        '''test failing if dataset code is not a list'''
        app = IniDatasetcodeGenerator()
        info = {'GENERATOR': 'generate2.ini',
                'DATASET_CODE': '20120320164249179-361885'
        }
        exit_code, info = app.main(info, self.log)
        assert exit_code == 0
        assert os.path.exists(self.tmp_dir + "/generate2.ini_0")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_run_guse_generator']
    unittest.main()
