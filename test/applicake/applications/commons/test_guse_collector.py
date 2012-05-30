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
        a = [10,9,8,7,6,5,4,3,2,1]
        b = ['s1','s2','s3','s4','s5','s6','s7','s8','s9','s10']
        c = ['s1','s1','s1','s2','s2','s2','s3','s3','s3','s10']
        for idx in range(0,10):
            path = '_'.join([self.collector_file,"%s" % idx])
            x = a[idx]
            y = b[idx]
            z = c[idx]
            fh = open(path,'w+')            
            fh.write("""COMMENT = 'hello','world'
    STORAGE = file
    OUTPUT = /fake/output.ini 
    LOG_LEVEL = INFO
    BASEDIR = %s
    JOB_IDX = 15
    DATASET_CODE = 20120320164249179-361885,20120320164249179-361886,20120320164249179-361887
    COLLECTOR_IDX = %s
    P1 = %s
    P2 = %s
    P3 = %s
""" % (self.tmp_dir,idx,x,y,z))
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
                    runner.COMMENT: [
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
                    runner.DATASET_CODE: [
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
                    runner.WORKDIR: 'GuseCollector', 
                    runner.NAME: 'GuseCollector', 
                    runner.COLLECTOR_IDX: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    runner.STORAGE: 'memory', # the default set in the runner
                    runner.JOB_IDX: ['15', '15', '15', '15', '15', '15', '15', '15', '15', '15'], 
                    'P1': ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1'],
                    'P2': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10'],
                    'P3': ['s1','s1','s1','s2', 's2', 's2', 's3', 's3', 's3', 's10']
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
                    runner.COMMENT: [
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
                    runner.DATASET_CODE: [
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
                    runner.WORKDIR: 'GuseCollector', 
                    runner.NAME: 'GuseCollector', 
                    runner.STORAGE: 'file',
                    'COLLECTOR_IDX': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    runner.JOB_IDX: ['15', '15', '15', '15', '15', '15', '15', '15', '15', '15'], 
                    'P1': ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1'],
                    'P2': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10'],
                    'P3': ['s1','s1','s1', 's2', 's2', 's2', 's3', 's3', 's3', 's10']                    
                    }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(dic, expected)
                                   
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_guse_collector']
    unittest.main()