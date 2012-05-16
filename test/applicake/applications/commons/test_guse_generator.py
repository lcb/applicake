'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
from applicake.framework.runner import GeneratorRunner
from applicake.applications.proteomics.openbis.generator import GuseGenerator


class Test(unittest.TestCase):


    def setUp(self):
        self.input = 'echo_test.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)       
        fh = open(self.input,'w+')
        fh.write("""COMMENT = 'hello','world'
STORAGE = file
LOG_LEVEL = INFO
BASEDIR = %s
DATASET_CODE = 20120320164249179-361885,20120320164249179-361886,20120320164249179-361887
""" % self.tmp_dir)
        fh.close()
        self.output = 'output.ini'


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_guse_generator(self):
        runner = GeneratorRunner()
        wrapper = GuseGenerator()
        sys.argv = ['', '-i', self.input, '--%s' % runner.GENERATOR,self.output]
        exit_code = runner(sys.argv,wrapper)        
        assert 0 == exit_code
        print runner.info[runner.CREATED_FILES]
        assert 9 == len(runner.info[runner.CREATED_FILES]) # 6 output.ini.[IDX] + out/err/log
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_run_guse_generator']
    unittest.main()