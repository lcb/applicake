'''
Created on Apr 18, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
from applicake.framework.confighandler import ConfigHandler
from applicake.framework.logger import Logger
from applicake.framework.runner import ApplicationRunner
from applicake.applications.commons.collector import GuseCollector
from StringIO import StringIO

class Test(unittest.TestCase):


    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=log_stream)
        self.collector_file = 'echo_test.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)       
        self.range = range(0,10)
        for idx in range(0,10):
            path = '_'.join([self.collector_file,"%s" % idx])
            fh = open(path,'w+')            
            fh.write("""COMMENT = 'hello','world'
    STORAGE = file
    OUTPUT = /fake/output.ini 
    LOG_LEVEL = INFO
    BASEDIR = %s
    DATASET_CODE = 20120320164249179-361885,20120320164249179-361886,20120320164249179-361887
    COLLECTOR_IDX = %s
""" % (self.tmp_dir,idx))
            fh.close()
            self.output = 'test_output.ini'


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_guse_collector_1(self):
        ''' Test with only collector and output flag'''
        runner = ApplicationRunner()
        app = GuseCollector()
        sys.argv = ['', '--%s' % app.COLLECTOR, self.collector_file, '-o',self.output]
        exit_code = runner(sys.argv,app)        
        self.assertTrue(exit_code ==0,'found [%s]\nexpected [%s]' % (exit_code,0)) 
        runner.info[runner.COLLECTOR_IDX] = self.range
        config = ConfigHandler().read(self.log, self.output)
        # converts ConfigObj to dict -> needed for comparison
        dic = dict(config)
        # for assert 'BASEDIR has to be removed because it contains full path
        dic.pop(runner.BASEDIR)      
        expected = {
                    runner.COMMENT: ['hello', 'world'], 
                    runner.DATASET_CODE: ['20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887'], 
                    runner.WORKDIR: '1/GuseCollector', 
                    runner.LOG_LEVEL: 'DEBUG', # the default set in the runner
                    runner.NAME: 'GuseCollector', 
                    runner.COLLECTOR: ['echo_test.ini'], 
                    runner.COLLECTOR_IDX: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    runner.STORAGE: 'memory', # the default set in the runner
                    runner.JOB_IDX: '1', 
                    runner.OUTPUT: self.output, 
                    runner.CREATED_FILES: [],
                    }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(dic, expected)

    def test_guse_collector_2(self):
        ''' Test with collector, output flag and other cmdline flags to set defaults'''
        runner = ApplicationRunner()
        wrapper = GuseCollector()
#        sys.argv = ['run_echo.py', '-c', self.collector_file, '-o',self.output,'-l','INFO','-s','file'] #for ApplicationArgsHandler()
        sys.argv = ['', '--%s' % runner.COLLECTOR, self.collector_file, '-o',self.output,'-l','INFO','-s','file'] # for BasicArgsHandler()
        exit_code = runner(sys.argv,wrapper)        
        assert 0 == exit_code
        runner.info['COLLECTOR_IDX'] = self.range
        config = ConfigHandler().read(self.log, self.output)
        # converts ConfigObj to dict -> needed for comparison
        dic = dict(config)
        # for assert 'BASEDIR has to be removed because it contains full path
        dic.pop(runner.BASEDIR)      
        expected = {
                    runner.COMMENT: ['hello', 'world'], 
                    runner.DATASET_CODE: ['20120320164249179-361885', '20120320164249179-361886', '20120320164249179-361887'], 
                    runner.WORKDIR: '1/GuseCollector', 
                    runner.LOG_LEVEL: 'INFO',
                    runner.NAME: 'GuseCollector', 
                    runner.COLLECTOR: ['echo_test.ini'], 
                    'COLLECTOR_IDX': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    runner.STORAGE: 'file',
                    runner.JOB_IDX: '1', 
                    runner.OUTPUT: self.output, 
                    runner.CREATED_FILES: ['GuseCollector.out', 'GuseCollector.err', 'GuseCollector.log'],
                    }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(dic, expected)
                                   
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_guse_collector']
    unittest.main()