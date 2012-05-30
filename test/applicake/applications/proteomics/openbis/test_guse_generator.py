'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
from applicake.framework.logger import Logger
from applicake.framework.runner import GeneratorRunner
from applicake.applications.proteomics.openbis.generator import GuseGenerator
from StringIO import StringIO

class Test(unittest.TestCase):


    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=log_stream)                
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


    def test_guse_generator__1(self):
        runner = GeneratorRunner()
        app = GuseGenerator()
        sys.argv = ['', '-i', self.input, '--%s' % runner.GENERATOR,self.output]
        exit_code = runner(sys.argv,app)        
        assert 0 == exit_code
        print runner.info[runner.COPY_TO_WD]
        assert 9 == len(runner.info[runner.COPY_TO_WD]) # 6 output.ini.[IDX] + out/err/log
        
        
    def test_guse_generator__2(self):
        '''test failing if dataset code is not a list'''
        app = GuseGenerator()
        info = {
                'DATASET_CODE':'20120320164249179-361885'
                }
        exit_code, info = app.main(info, self.log)
        assert exit_code == 1
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_run_guse_generator']
    unittest.main()